#!/usr/bin/env python
"""Import blog entries produced by ``extract_blog_entries.py`` into the database.

For each entry in the JSON file:

* Look up (or create) an :class:`authors.models.AuthorProfile` by slug.
* Look up (or create) a :class:`djangocms_stories.models.PostCategory` per
  category, keyed on the English slug.
* Look up (or create) a :class:`djangocms_stories.models.Post` keyed on the
  publication date and the English title.
* Create the matching :class:`djangocms_stories.models.PostContent` (English),
  drop a single ``MDTextPlugin`` carrying the markdown body into its ``content``
  placeholder, and (when ``djangocms-versioning`` is installed) publish the
  resulting version.

The script is idempotent: re-running it skips entries that already exist.

Usage::

    docker compose exec web python scripts/import_blog_entries.py blogs.json
    # or via do.sh:
    ./do.sh exec web python scripts/import_blog_entries.py blogs.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, time
from pathlib import Path

# --- Django bootstrap ------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

import django  # noqa: E402

django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.db import transaction  # noqa: E402
from django.utils import timezone  # noqa: E402
from django.utils.text import slugify  # noqa: E402

from cms.api import add_plugin  # noqa: E402
from cms.utils.placeholder import get_placeholder_from_slot  # noqa: E402

from authors.models import AuthorProfile  # noqa: E402
from djangocms_stories.cms_appconfig import StoriesConfig  # noqa: E402
from djangocms_stories.models import Post, PostCategory, PostContent  # noqa: E402

User = get_user_model()

LANGUAGE = "en"
MARKDOWN_PLUGIN_TYPE = "MDTextPlugin"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_date(date_str: str) -> datetime:
    """Convert 'YYYY-MM-DD' to a timezone-aware datetime at local midnight."""
    naive = datetime.combine(datetime.strptime(date_str, "%Y-%m-%d").date(), time.min)
    if timezone.is_naive(naive):
        return timezone.make_aware(naive, timezone.get_current_timezone())
    return naive


def get_or_create_author(author_data: dict[str, str]) -> AuthorProfile:
    """Find an AuthorProfile by slug, or create it (and its inactive User)."""
    slug = author_data["slug"]
    try:
        return AuthorProfile.objects.get(slug=slug)
    except AuthorProfile.DoesNotExist:
        profile = AuthorProfile(slug=slug, name=author_data["name"])
        profile.save()  # save() auto-provisions the inactive User
        return profile


def get_or_create_category(
    cat_data: dict[str, str],
    app_config: StoriesConfig,
) -> PostCategory:
    """Find a PostCategory by english slug, or create it."""
    slug = cat_data["slug"]
    qs = PostCategory.objects.translated(LANGUAGE, slug=slug).filter(
        app_config=app_config
    )
    existing = qs.first()
    if existing is not None:
        return existing
    cat = PostCategory(app_config=app_config)
    cat.set_current_language(LANGUAGE)
    cat.name = cat_data["name"]
    cat.slug = slug
    cat.save()
    return cat


def find_existing_post(date: datetime, title: str) -> Post | None:
    """Return an existing Post matching the (date, english title) pair."""
    # Use the admin manager so we see drafts too — we want full idempotency.
    qs = PostContent.admin_manager.filter(
        language=LANGUAGE,
        title=title,
        post__date_published__date=date.date(),
    ).select_related("post")
    pc = qs.first()
    return pc.post if pc is not None else None


def make_unique_slug(base: str) -> str:
    """Generate a slug for a new PostContent that doesn't collide with siblings."""
    base = base or "post"
    used = set(
        PostContent.admin_manager.filter(language=LANGUAGE).values_list(
            "slug", flat=True
        )
    )
    candidate = base
    i = 2
    while candidate in used:
        candidate = f"{base}-{i}"
        i += 1
    return candidate


def publish_if_versioned(content_obj, user) -> None:
    """If djangocms-versioning is installed, publish the draft just created."""
    try:
        from djangocms_versioning.models import Version
    except ImportError:
        return
    try:
        version = Version.objects.get_for_content(content_obj)
    except Version.DoesNotExist:
        return
    # State machine guard: only publish if currently DRAFT.
    from djangocms_versioning import constants

    if version.state == constants.DRAFT:
        version.publish(user)


def resolve_app_config(namespace: str | None) -> StoriesConfig:
    qs = StoriesConfig.objects.all()
    if namespace:
        try:
            return qs.get(namespace=namespace)
        except StoriesConfig.DoesNotExist as exc:
            raise SystemExit(
                f"error: no StoriesConfig found with namespace={namespace!r}"
            ) from exc
    configs = list(qs)
    if not configs:
        raise SystemExit(
            "error: no StoriesConfig defined; create one in the admin first"
        )
    if len(configs) > 1:
        names = ", ".join(c.namespace for c in configs)
        raise SystemExit(
            "error: multiple StoriesConfig instances exist "
            f"({names}); pass --app-config <namespace>"
        )
    return configs[0]


def resolve_user(username: str | None):
    if username:
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist as exc:
            raise SystemExit(f"error: no user with username={username!r}") from exc
    user = (
        User.objects.filter(is_superuser=True, is_active=True)
        .order_by("pk")
        .first()
    )
    if user is None:
        raise SystemExit(
            "error: no active superuser found; pass --user <username>"
        )
    return user


# ---------------------------------------------------------------------------
# Import core
# ---------------------------------------------------------------------------

def import_entry(
    entry: dict,
    app_config: StoriesConfig,
    user,
    *,
    dry_run: bool = False,
) -> str:
    """Import a single JSON entry. Returns one of: 'created', 'skipped', 'error:...'."""
    title = entry.get("title", "") or ""
    if not title.strip():
        return "error:no-title"
    date = parse_date(entry["date"])

    existing = find_existing_post(date, title)
    if existing is not None:
        return "skipped"

    if dry_run:
        return "created"

    author_data = entry.get("author")
    if not author_data:
        return "error:no-author"
    author_profile = get_or_create_author(author_data)

    categories = [
        get_or_create_category(c, app_config)
        for c in (entry.get("categories") or [])
    ]

    with transaction.atomic():
        post = Post(
            app_config=app_config,
            author=author_profile.user,
            date_published=date,
        )
        post.save()
        if categories:
            post.categories.set(categories)

        slug = make_unique_slug(slugify(title))
        pc = PostContent.objects.with_user(user).create(
            post=post,
            language=LANGUAGE,
            title=title,
            slug=slug,
            abstract=entry.get("lead", "") or "",
        )
        

        body = entry.get("content", "") or ""
        if body:
            placeholder = get_placeholder_from_slot(pc.placeholders, "Blog Content")
            add_plugin(
                placeholder=placeholder,
                plugin_type=MARKDOWN_PLUGIN_TYPE,
                language=LANGUAGE,
                body=body,
            )

        publish_if_versioned(pc, user)

    return "created"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("json_file", help="Path to the JSON produced by extract_blog_entries.py")
    ap.add_argument(
        "--app-config",
        help="StoriesConfig namespace to attach posts/categories to",
    )
    ap.add_argument(
        "--user",
        help="Username to credit as the version creator (default: first active superuser)",
    )
    ap.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only import the first N entries (handy for testing)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't write anything; just report what would be done",
    )
    args = ap.parse_args()

    json_path = Path(args.json_file)
    if not json_path.is_file():
        raise SystemExit(f"error: file not found: {json_path}")

    with json_path.open(encoding="utf-8") as fh:
        entries = json.load(fh)
    if args.limit is not None:
        entries = entries[: args.limit]

    app_config = resolve_app_config(args.app_config)
    user = resolve_user(args.user)
    print(
        f"using app_config={app_config.namespace!r}, version-author={user.username!r}, "
        f"language={LANGUAGE!r}",
        file=sys.stderr,
    )

    counts = {"created": 0, "skipped": 0, "error": 0}
    for i, entry in enumerate(entries, 1):
        try:
            result = import_entry(entry, app_config, user, dry_run=args.dry_run)
        except Exception as exc:  # noqa: BLE001
            print(
                f"  [{i}/{len(entries)}] ERROR {entry.get('url', '?')}: {exc}",
                file=sys.stderr,
            )
            counts["error"] += 1
            continue
        if result.startswith("error"):
            counts["error"] += 1
            print(
                f"  [{i}/{len(entries)}] {result} {entry.get('url', '?')}",
                file=sys.stderr,
            )
        else:
            counts[result] += 1
        if i % 25 == 0 or i == len(entries):
            print(
                f"  progress: {i}/{len(entries)} "
                f"(created={counts['created']} skipped={counts['skipped']} error={counts['error']})",
                file=sys.stderr,
            )

    verb = "would create" if args.dry_run else "created"
    print(
        f"done: {verb}={counts['created']}, skipped={counts['skipped']}, errors={counts['error']}",
        file=sys.stderr,
    )
    return 0 if counts["error"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
