#!/usr/bin/env python3
"""Extract blog entries (title, date, URL, lead, content) from www.django-cms.org.

The site's sitemap.xml only lists the /en/blog/ landing page, not the
individual posts, so this script:

  1. Reads sitemap.xml and locates any blog landing pages.
  2. Walks the paginated blog index for each landing page.
  3. Parses each article card for title, publication date, and URL.
  4. Fetches each post page and extracts the lead and body as Markdown.

Output is JSON on stdout (or to --output). Pass --csv for CSV instead
(CSV omits the long markdown fields). Pass --no-content to skip step 4.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

SITE = "https://www.django-cms.org"
SITEMAP_URL = f"{SITE}/sitemap.xml"
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
USER_AGENT = "django-cms-blog-extractor/1.0 (+https://www.django-cms.org)"

# /en/blog/YYYY/MM/DD/slug/
POST_URL_RE = re.compile(r"^/[a-z]{2}/blog/\d{4}/\d{2}/\d{2}/[^/]+/?$")


@dataclass
class BlogEntry:
    title: str
    date: str  # ISO 8601 (YYYY-MM-DD)
    url: str
    author: dict[str, str] | None = None  # {"name": ..., "slug": ...}
    categories: list[dict[str, str]] = field(default_factory=list)  # [{"name", "slug"}, ...]
    lead: str = ""
    content: str = ""


# ---------------------------------------------------------------------------
# Minimal HTML -> Markdown converter (stdlib only).
# Targets the tags actually emitted by the django-cms blog: p, h1-h6,
# strong/b, em/i, a, code, pre, ul/ol/li, blockquote, br, hr, img, table.
# ---------------------------------------------------------------------------

VOID_HTML_ELEMENTS = {"br", "hr", "img", "meta", "link", "input", "source"}


class _Node:
    __slots__ = ("tag", "attrs", "children")

    def __init__(self, tag: str, attrs: dict[str, str] | None = None) -> None:
        self.tag = tag
        self.attrs = attrs or {}
        self.children: list[_Node | str] = []


class _DOMBuilder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = _Node("root")
        self.stack: list[_Node] = [self.root]

    def handle_starttag(self, tag, attrs):
        node = _Node(tag, {k: (v or "") for k, v in attrs})
        self.stack[-1].children.append(node)
        if tag not in VOID_HTML_ELEMENTS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        node = _Node(tag, {k: (v or "") for k, v in attrs})
        self.stack[-1].children.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return
        # Unmatched closing tag — ignore.

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def _node_text(node: _Node) -> str:
    out: list[str] = []
    for c in node.children:
        if isinstance(c, str):
            out.append(c)
        else:
            out.append(_node_text(c))
    return "".join(out)


def _find_by_class(node: _Node, tag: str, cls: str) -> _Node | None:
    for c in node.children:
        if isinstance(c, str):
            continue
        if c.tag == tag and cls in c.attrs.get("class", "").split():
            return c
        found = _find_by_class(c, tag, cls)
        if found is not None:
            return found
    return None


def _find_all(node: _Node, tag: str) -> list[_Node]:
    found: list[_Node] = []
    for c in node.children:
        if isinstance(c, str):
            continue
        if c.tag == tag:
            found.append(c)
        found.extend(_find_all(c, tag))
    return found


def _render_inline(children: list[_Node | str]) -> str:
    parts: list[str] = []
    for child in children:
        if isinstance(child, str):
            parts.append(child)
            continue
        tag = child.tag
        if tag in ("strong", "b"):
            inner = _render_inline(child.children).strip()
            parts.append(f"**{inner}**" if inner else "")
        elif tag in ("em", "i"):
            inner = _render_inline(child.children).strip()
            parts.append(f"*{inner}*" if inner else "")
        elif tag == "code":
            parts.append(f"`{_node_text(child)}`")
        elif tag == "a":
            href = child.attrs.get("href", "")
            text = _render_inline(child.children).strip()
            if href and text:
                parts.append(f"[{text}]({href})")
            else:
                parts.append(text or href)
        elif tag == "br":
            parts.append("  \n")
        elif tag == "img":
            src = child.attrs.get("src", "")
            alt = child.attrs.get("alt", "")
            if src:
                parts.append(f"![{alt}]({src})")
        elif tag in ("span", "u", "small", "sub", "sup", "font"):
            parts.append(_render_inline(child.children))
        else:
            parts.append(_render_inline(child.children))
    return "".join(parts)


def _collapse_ws(text: str) -> str:
    return re.sub(r"[ \t\r\n]+", " ", text).strip()


def _render_blocks(children: list[_Node | str], list_indent: int = 0) -> list[str]:
    blocks: list[str] = []
    inline_buf: list[str] = []

    def flush() -> None:
        if not inline_buf:
            return
        text = _collapse_ws("".join(inline_buf))
        if text:
            blocks.append(text)
        inline_buf.clear()

    for child in children:
        if isinstance(child, str):
            inline_buf.append(child)
            continue
        tag = child.tag
        if tag == "p":
            flush()
            text = _collapse_ws(_render_inline(child.children))
            if text:
                blocks.append(text)
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            flush()
            level = int(tag[1])
            text = _collapse_ws(_render_inline(child.children))
            if text:
                blocks.append("#" * level + " " + text)
        elif tag == "pre":
            flush()
            inner: _Node = child
            non_blank = [
                c for c in child.children
                if not (isinstance(c, str) and not c.strip())
            ]
            if (
                len(non_blank) == 1
                and not isinstance(non_blank[0], str)
                and non_blank[0].tag == "code"
            ):
                inner = non_blank[0]
            code = _node_text(inner).strip("\n")
            blocks.append("```\n" + code + "\n```")
        elif tag == "ul":
            flush()
            rendered = _render_list(child, ordered=False, indent=list_indent)
            if rendered:
                blocks.append(rendered)
        elif tag == "ol":
            flush()
            rendered = _render_list(child, ordered=True, indent=list_indent)
            if rendered:
                blocks.append(rendered)
        elif tag == "blockquote":
            flush()
            inner_md = "\n\n".join(_render_blocks(child.children))
            if inner_md:
                blocks.append("\n".join("> " + ln for ln in inner_md.split("\n")))
        elif tag == "hr":
            flush()
            blocks.append("---")
        elif tag == "img":
            flush()
            src = child.attrs.get("src", "")
            alt = child.attrs.get("alt", "")
            if src:
                blocks.append(f"![{alt}]({src})")
        elif tag in ("div", "section", "article", "figure"):
            flush()
            blocks.extend(_render_blocks(child.children, list_indent))
        elif tag == "table":
            flush()
            rendered = _render_table(child)
            if rendered:
                blocks.append(rendered)
        elif tag in ("script", "style", "noscript"):
            continue
        else:
            inline_buf.append(_render_inline([child]))
    flush()
    return blocks


def _render_list(node: _Node, ordered: bool, indent: int) -> str:
    lines: list[str] = []
    counter = 0
    for child in node.children:
        if isinstance(child, str) or child.tag != "li":
            continue
        counter += 1
        marker = f"{counter}. " if ordered else "- "
        sub_blocks = _render_blocks(child.children, list_indent=indent + 1)
        if not sub_blocks:
            continue
        prefix = " " * indent + marker
        cont = " " * (indent + len(marker))
        first = sub_blocks[0]
        first_lines = first.split("\n")
        out = prefix + first_lines[0]
        for ln in first_lines[1:]:
            out += "\n" + cont + ln
        for blk in sub_blocks[1:]:
            out += "\n\n" + "\n".join(cont + ln for ln in blk.split("\n"))
        lines.append(out)
    return "\n".join(lines)


def _render_table(node: _Node) -> str:
    rows: list[list[str]] = []
    for tr in _find_all(node, "tr"):
        cells: list[str] = []
        for cell in tr.children:
            if isinstance(cell, str) or cell.tag not in ("td", "th"):
                continue
            cells.append(_collapse_ws(_render_inline(cell.children)))
        if cells:
            rows.append(cells)
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    out = ["| " + " | ".join(rows[0]) + " |"]
    out.append("| " + " | ".join("---" for _ in range(width)) + " |")
    for r in rows[1:]:
        out.append("| " + " | ".join(r) + " |")
    return "\n".join(out)


def html_node_to_markdown(node: _Node) -> str:
    blocks = _render_blocks(node.children)
    return "\n\n".join(b for b in blocks if b).strip()


AUTHOR_SLUG_RE = re.compile(r"/blog/author/([^/]+)/?$")
CATEGORY_SLUG_RE = re.compile(r"/blog/category/([^/]+)/?$")


def _extract_categories(article: _Node) -> list[dict[str, str]]:
    """Find <p class="category"><a href=".../blog/category/<slug>/">Name</a>...</p>."""
    cat_p = _find_by_class(article, "p", "category")
    if cat_p is None:
        return []
    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for a in _find_all(cat_p, "a"):
        href = a.attrs.get("href", "")
        m = CATEGORY_SLUG_RE.search(href)
        if not m:
            continue
        slug = m.group(1)
        if slug in seen:
            continue
        seen.add(slug)
        name = _collapse_ws(_node_text(a))
        if name:
            out.append({"name": name, "slug": slug})
    return out


def _extract_author(article: _Node) -> dict[str, str] | None:
    """Find <p class="author"><a href="/.../blog/author/<slug>/">Name</a></p>."""
    author_p = _find_by_class(article, "p", "author")
    if author_p is None:
        return None
    for a in _find_all(author_p, "a"):
        href = a.attrs.get("href", "")
        m = AUTHOR_SLUG_RE.search(href)
        if not m:
            continue
        name = _collapse_ws(_node_text(a))
        if name:
            return {"name": name, "slug": m.group(1)}
    return None


def extract_post_fields(
    post_html: str,
) -> tuple[str, str, dict[str, str] | None, list[dict[str, str]]]:
    """Return (lead_md, content_md, author, categories) extracted from a post page."""
    builder = _DOMBuilder()
    builder.feed(post_html)
    article = _find_by_class(builder.root, "article", "aldryn-newsblog-article")
    root = article if article is not None else builder.root
    lead_node = _find_by_class(root, "div", "lead")
    content_node = _find_by_class(root, "div", "content")
    lead_md = html_node_to_markdown(lead_node) if lead_node is not None else ""
    content_md = html_node_to_markdown(content_node) if content_node is not None else ""
    author = _extract_author(root)
    categories = _extract_categories(root)
    return lead_md, content_md, author, categories


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def find_blog_landing_pages(sitemap_xml: str) -> list[str]:
    """Return URLs in the sitemap whose path ends with /blog/."""
    root = ET.fromstring(sitemap_xml)
    landings = []
    for url in root.findall("sm:url/sm:loc", SITEMAP_NS):
        loc = (url.text or "").strip()
        if re.search(r"/[a-z]{2}/blog/?$", loc):
            landings.append(loc.rstrip("/") + "/")
    return landings


class BlogIndexParser(HTMLParser):
    """Pull (url, title, date_text) tuples out of an aldryn-newsblog index page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.entries: list[tuple[str, str, str]] = []
        self._in_list = False
        self._list_depth = 0
        self._in_article = False
        self._article_depth = 0
        self._in_title_a = False
        self._in_date_p = False
        self._current_url: str | None = None
        self._current_title_parts: list[str] = []
        self._current_date_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_d = dict(attrs)
        classes = (attrs_d.get("class") or "").split()

        # Only consider articles inside the main listing wrapper, not sidebar widgets.
        if tag == "div" and "aldryn-newsblog-list" in classes and not self._in_list:
            self._in_list = True
            self._list_depth = 1
            return
        if self._in_list and tag == "div":
            self._list_depth += 1

        if not self._in_list:
            return

        if tag == "article" and "aldryn-newsblog-article" in classes:
            self._in_article = True
            self._article_depth = 1
            self._current_url = None
            self._current_title_parts = []
            self._current_date_parts = []
            return

        if not self._in_article:
            return

        # Track nesting so we know when the article closes.
        if tag == "article":
            self._article_depth += 1

        if (
            tag == "a"
            and self._current_url is None
            and POST_URL_RE.match(attrs_d.get("href") or "")
        ):
            self._current_url = attrs_d["href"]
            self._in_title_a = True
        elif tag == "p" and "date" in classes:
            self._in_date_p = True

    def handle_endtag(self, tag: str) -> None:
        if self._in_list and tag == "div" and not self._in_article:
            self._list_depth -= 1
            if self._list_depth == 0:
                self._in_list = False
            return
        if not self._in_article:
            return
        if tag == "a" and self._in_title_a:
            self._in_title_a = False
        elif tag == "p" and self._in_date_p:
            self._in_date_p = False
        elif tag == "article":
            self._article_depth -= 1
            if self._article_depth == 0:
                if self._current_url:
                    title = " ".join(
                        "".join(self._current_title_parts).split()
                    ).strip()
                    date_text = " ".join(
                        "".join(self._current_date_parts).split()
                    ).strip()
                    self.entries.append((self._current_url, title, date_text))
                self._in_article = False

    def handle_data(self, data: str) -> None:
        if self._in_title_a:
            self._current_title_parts.append(data)
        elif self._in_date_p:
            self._current_date_parts.append(data)


def parse_date(text: str, fallback_url: str) -> str:
    """Return YYYY-MM-DD. Prefer the URL date, fall back to the visible label."""
    m = re.search(r"/blog/(\d{4})/(\d{2})/(\d{2})/", fallback_url)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    for fmt in ("%B %d, %Y", "%b. %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    return text  # give up: return the raw label


def collect_entries(landing_url: str, max_pages: int | None = None) -> list[BlogEntry]:
    seen: set[str] = set()
    entries: list[BlogEntry] = []
    page = 1
    while True:
        if max_pages is not None and page > max_pages:
            break
        page_url = landing_url if page == 1 else f"{landing_url}?page={page}"
        try:
            html = fetch(page_url)
        except Exception as exc:  # noqa: BLE001
            print(f"warn: failed to fetch {page_url}: {exc}", file=sys.stderr)
            break

        parser = BlogIndexParser()
        parser.feed(html)
        if not parser.entries:
            break  # past the last page

        new_on_page = 0
        for href, title, date_text in parser.entries:
            full_url = urljoin(landing_url, href)
            if full_url in seen:
                continue
            seen.add(full_url)
            new_on_page += 1
            entries.append(
                BlogEntry(
                    title=title,
                    date=parse_date(date_text, full_url),
                    url=full_url,
                )
            )

        if new_on_page == 0:
            break
        page += 1
    return entries


def _populate_post_bodies(entries: list[BlogEntry], workers: int) -> None:
    """Fetch each post page in parallel and fill in entry.lead / entry.content."""
    total = len(entries)
    done = 0

    def work(
        entry: BlogEntry,
    ) -> tuple[
        BlogEntry,
        str,
        str,
        dict[str, str] | None,
        list[dict[str, str]],
        str | None,
    ]:
        try:
            html = fetch(entry.url)
            lead, content, author, categories = extract_post_fields(html)
            return entry, lead, content, author, categories, None
        except Exception as exc:  # noqa: BLE001
            return entry, "", "", None, [], str(exc)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(work, e) for e in entries]
        for fut in as_completed(futures):
            entry, lead, content, author, categories, err = fut.result()
            done += 1
            if err:
                print(
                    f"warn: failed to fetch {entry.url}: {err}",
                    file=sys.stderr,
                )
            else:
                entry.lead = lead
                entry.content = content
                entry.author = author
                entry.categories = categories
            if done % 25 == 0 or done == total:
                print(f"  fetched {done}/{total} posts", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sitemap", default=SITEMAP_URL, help="Sitemap URL")
    ap.add_argument(
        "--landing",
        action="append",
        help="Override: blog landing URL to crawl (repeatable). "
        "If omitted, landings are discovered from the sitemap.",
    )
    ap.add_argument("--max-pages", type=int, default=None)
    ap.add_argument(
        "--csv",
        action="store_true",
        help="Emit CSV instead of JSON (omits lead/content columns)",
    )
    ap.add_argument("--output", "-o", help="Write to file instead of stdout")
    ap.add_argument(
        "--no-content",
        action="store_true",
        help="Skip per-post fetches; emit only title/date/url.",
    )
    ap.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Parallel workers for per-post fetches (default: 8)",
    )
    args = ap.parse_args()

    if args.landing:
        landings = [u.rstrip("/") + "/" for u in args.landing]
    else:
        try:
            sitemap_xml = fetch(args.sitemap)
        except Exception as exc:  # noqa: BLE001
            print(f"error: could not fetch sitemap {args.sitemap}: {exc}", file=sys.stderr)
            return 1
        landings = find_blog_landing_pages(sitemap_xml)
        if not landings:
            print(
                "error: no blog landing page found in sitemap; pass --landing",
                file=sys.stderr,
            )
            return 1

    all_entries: list[BlogEntry] = []
    for landing in landings:
        print(f"crawling {landing} ...", file=sys.stderr)
        all_entries.extend(collect_entries(landing, max_pages=args.max_pages))

    # Newest first.
    all_entries.sort(key=lambda e: e.date, reverse=True)

    if not args.no_content and all_entries:
        _populate_post_bodies(all_entries, workers=max(1, args.workers))

    out = open(args.output, "w", encoding="utf-8") if args.output else sys.stdout
    try:
        if args.csv:
            writer = csv.DictWriter(out, fieldnames=["date", "title", "url"])
            writer.writeheader()
            for e in all_entries:
                writer.writerow({"date": e.date, "title": e.title, "url": e.url})
        else:
            json.dump([asdict(e) for e in all_entries], out, indent=2, ensure_ascii=False)
            out.write("\n")
    finally:
        if args.output:
            out.close()

    print(f"extracted {len(all_entries)} blog entries", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
