#!/usr/bin/env python
"""Seed the redirects app from a live sitemap.

Reads ``https://www.django-cms.org/sitemap.xml`` (a flat ``<urlset>`` or a
``<sitemapindex>`` that points at further sitemaps), and for every ``<loc>``
creates a :class:`django.contrib.redirects.models.Redirect` whose ``old_path``
is the URL's path component and whose ``new_path`` is ``/`` (the home page).

The script is idempotent: a redirect is only created when one does not already
exist for the same site and ``old_path``.

Usage::

    docker compose exec web python scripts/import_sitemap_redirects.py
    # or via do.sh:
    ./do.sh exec web python scripts/import_sitemap_redirects.py

    # override the sitemap URL or the redirect target:
    python scripts/import_sitemap_redirects.py --url https://example.com/sitemap.xml --target /
    # preview without writing to the database:
    python scripts/import_sitemap_redirects.py --dry-run
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree

# --- Django bootstrap ------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

import django  # noqa: E402

django.setup()

import requests  # noqa: E402
from django.conf import settings  # noqa: E402
from django.contrib.redirects.models import Redirect  # noqa: E402
from django.contrib.sites.models import Site  # noqa: E402

DEFAULT_SITEMAP_URL = "https://www.django-cms.org/sitemap.xml"
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def fetch(url: str) -> bytes:
    """Download ``url`` and return its raw body."""
    response = requests.get(url, timeout=30, headers={"User-Agent": "sitemap-redirect-importer"})
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
            locations.append(loc.text.strip())
    return locations


def to_old_path(location: str) -> str:
    """Extract the request path (with query string) used as ``old_path``."""
    parts = urlparse(location)
    path = parts.path or "/"
    if parts.query:
        path = f"{path}?{parts.query}"
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_SITEMAP_URL, help="Sitemap URL to read.")
    parser.add_argument("--target", default="/", help="new_path for each redirect (default: /).")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without writing to the database.",
    )
    args = parser.parse_args()

    site = Site.objects.get(pk=settings.SITE_ID)
    print(f"Reading {args.url} …")
    locations = collect_locations(args.url)

    # De-duplicate paths while preserving order (a sitemap may list a URL twice).
    old_paths: list[str] = []
    seen: set[str] = set()
    for location in locations:
        old_path = to_old_path(location)
        if old_path not in seen:
            seen.add(old_path)
            old_paths.append(old_path)

    print(f"Found {len(old_paths)} unique path(s); target site: {site.domain} (#{site.pk}).")

    created = skipped = 0
    for old_path in old_paths:
        if Redirect.objects.filter(site=site, old_path=old_path).exists():
            skipped += 1
            continue
        if args.dry_run:
            print(f"[dry-run] would create {old_path} -> {args.target}")
        else:
            Redirect.objects.create(site=site, old_path=old_path, new_path=args.target)
            print(f"created {old_path} -> {args.target}")
        created += 1

    verb = "would create" if args.dry_run else "created"
    print(f"Done. {verb} {created}, skipped {skipped} (already present).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
