#!/usr/bin/env python
"""Propose a meta description for every page listed in a site's sitemap.

For each ``<loc>`` reachable from the sitemap the script downloads the page,
extracts its visible text and current ``<title>`` / meta description, and asks
the OpenAI Chat Completions API to write a concise, SEO-friendly meta
description (~155 characters).

The OpenAI API key is read from the ``OPENAI_API_KEY`` environment variable.
No Django / database access is involved — results are printed and, optionally,
written to a CSV or JSON file.

Usage::

    export OPENAI_API_KEY=sk-...
    python scripts/propose_meta_descriptions.py
    python scripts/propose_meta_descriptions.py --url https://example.com/sitemap.xml
    python scripts/propose_meta_descriptions.py --limit 10 --output proposals.csv
    python scripts/propose_meta_descriptions.py --model gpt-4o-mini --output proposals.json
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from urllib.parse import urlparse
from xml.etree import ElementTree

import requests
from lxml import html as lxml_html

DEFAULT_SITEMAP_URL = "https://www.django-cms.org/sitemap.xml"
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-4o-mini"
USER_AGENT = "meta-description-proposer"

# Roughly how many characters of page text to feed the model. Enough for good
# context without paying for a whole long article.
DEFAULT_MAX_CHARS = 6000
# Target length of the proposed description; ~155 chars is the usual SERP limit.
TARGET_LENGTH = 155


# --- Sitemap ---------------------------------------------------------------
def fetch(url: str) -> bytes:
    """Download ``url`` and return its raw body."""
    response = requests.get(url, timeout=30, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    return response.content


def collect_locations(url: str, _seen: set[str] | None = None) -> list[str]:
    """Return every ``<loc>`` URL reachable from ``url``.

    Follows a ``<sitemapindex>`` into its child sitemaps; a plain ``<urlset>``
    yields its page URLs directly.
    """
    _seen = _seen if _seen is not None else set()
    if url in _seen:
        return []
    _seen.add(url)

    root = ElementTree.fromstring(fetch(url))
    locations: list[str] = []

    # A sitemap index: recurse into each referenced sitemap.
    sitemaps = root.findall(f"{SITEMAP_NS}sitemap/{SITEMAP_NS}loc")
    if sitemaps:
        for loc in sitemaps:
            if loc.text:
                locations.extend(collect_locations(loc.text.strip(), _seen))
        return locations

    # A plain urlset: collect each page location.
    for loc in root.findall(f"{SITEMAP_NS}url/{SITEMAP_NS}loc"):
        if loc.text:
            print(loc.text.strip())
            locations.append(loc.text.strip())
    return locations


# --- Page extraction -------------------------------------------------------
def extract_page(url: str, max_chars: int) -> dict[str, str]:
    """Return ``{title, description, text}`` for the page at ``url``."""
    tree = lxml_html.fromstring(fetch(url))

    title = (tree.findtext(".//title") or "").strip()

    description = ""
    for meta in tree.findall(".//meta"):
        if (meta.get("name") or "").lower() == "description":
            description = (meta.get("content") or "").strip()
            break

    # Drop non-content elements before reading the visible text.
    for bad in tree.xpath("//script | //style | //noscript | //template"):
        bad.getparent().remove(bad)
    body = tree.find(".//body")
    text = (body if body is not None else tree).text_content()
    text = re.sub(r"\s+", " ", text).strip()[:max_chars]

    return {"title": title, "description": description, "text": text}


# --- OpenAI ----------------------------------------------------------------
def propose_description(page: dict[str, str], *, api_key: str, model: str) -> str:
    """Ask the OpenAI API for a meta description for ``page``."""
    system = (
        "You are an SEO copywriter. Write a single compelling meta description "
        f"for the given web page in the page's own language. Keep it under "
        f"{TARGET_LENGTH} characters, written in plain prose with no quotes, no "
        "line breaks, and no surrounding markup. Summarise the page's actual "
        "content and entice a click. Respond with the description text only."
    )
    user = (
        f"URL: {page['url']}\n"
        f"Title: {page['title']}\n"
        f"Current meta description: {page['description'] or '(none)'}\n\n"
        f"Page content:\n{page['text']}"
    )

    response = requests.post(
        OPENAI_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "temperature": 0.7,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
        timeout=60,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    # Strip stray quotes/whitespace the model sometimes adds.
    return content.strip().strip('"').strip()


# --- Output ----------------------------------------------------------------
def write_output(rows: list[dict[str, str]], path: str) -> None:
    """Write ``rows`` to ``path`` as CSV or JSON (chosen by file extension)."""
    fields = ["url", "title", "current_description", "proposed_description"]
    if path.lower().endswith(".json"):
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, ensure_ascii=False, indent=2)
    else:
        with open(path, "w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", default=DEFAULT_SITEMAP_URL, help="Sitemap URL to read.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"OpenAI model (default: {DEFAULT_MODEL}).")
    parser.add_argument("--limit", type=int, default=0, help="Process at most N pages (0 = all).")
    parser.add_argument(
        "--max-chars",
        type=int,
        default=DEFAULT_MAX_CHARS,
        help=f"Page text sent to the model (default: {DEFAULT_MAX_CHARS}).",
    )
    parser.add_argument("--output", help="Write results to this .csv or .json file.")
    parser.add_argument("--delay", type=float, default=0.0, help="Seconds to wait between pages.")
    parser.add_argument(
        "--skip-blog",
        action="store_true",
        help="Skip pages whose path contains '/blog/' followed by something (e.g. posts).",
    )
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("error: set OPENAI_API_KEY in the environment.", file=sys.stderr)
        return 1

    print(f"Reading {args.url} …")
    locations = collect_locations(args.url)

    # De-duplicate while preserving order (a sitemap may list a URL twice).
    seen: set[str] = set()
    urls = [u for u in locations if not (u in seen or seen.add(u))]

    if args.skip_blog:
        blog = re.compile(r"/blog/.+")
        before = len(urls)
        urls = [u for u in urls if not blog.search(urlparse(u).path)]
        print(f"Skipped {before - len(urls)} '/blog/…' page(s).")

    if args.limit:
        urls = urls[: args.limit]
    print(f"Proposing meta descriptions for {len(urls)} page(s) using {args.model}.\n")

    rows: list[dict[str, str]] = []
    for index, url in enumerate(urls, start=1):
        path = urlparse(url).path or "/"
        try:
            page = extract_page(url, args.max_chars)
            page["url"] = url
            proposal = propose_description(page, api_key=api_key, model=args.model)
        except Exception as exc:  # noqa: BLE001 — report and carry on.
            print(f"[{index}/{len(urls)}] {path}\n  ! failed: {exc}\n", file=sys.stderr)
            continue

        rows.append(
            {
                "url": url,
                "title": page["title"],
                "current_description": page["description"],
                "proposed_description": proposal,
            }
        )
        print(f"[{index}/{len(urls)}] {path}\n  {proposal}\n")

        if args.delay:
            time.sleep(args.delay)

    if args.output:
        write_output(rows, args.output)
        print(f"Wrote {len(rows)} proposal(s) to {args.output}.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
