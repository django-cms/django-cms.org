from django import template
from django.conf import settings
from django.utils.html import strip_tags
from django.utils.text import Truncator

register = template.Library()


@register.simple_tag
def get_color_choices():
    """Get color style choices from settings"""
    return getattr(settings, 'DJANGOCMS_FRONTEND_COLOR_STYLE_CHOICES', [])


@register.filter
def color_choices_string(value):
    """Convert color choices from settings to string format for {% field %} tag"""
    choices = getattr(settings, 'DJANGOCMS_FRONTEND_COLOR_STYLE_CHOICES', [])
    # Convert to "value:Label,value:Label" format
    return ','.join([f"{choice[0]}:{choice[1]}" for choice in choices])


@register.filter
def make_choices(value):
    """Convert string format to choices tuple for ChoiceField
    Input: "value1:Label1,value2:Label2"
    Output: (('value1', 'Label1'), ('value2', 'Label2'))
    """
    if not value:
        return ()

    choices = []
    for item in value.split(','):
        if ':' in item:
            val, label = item.split(':', 1)
            choices.append((val.strip(), label.strip()))
    return tuple(choices)


@register.filter
def text_bg(background_context):
    """Map a background context to a class giving the text sufficient contrast.

    Delegates to Bootstrap's .text-bg-<color> helpers, whose text color is
    chosen at Sass compile time by color-contrast() against the actual hex
    value of each entry in $theme-colors. Apply on the same element that
    receives the bg-* class (e.g. next to instance.get_classes); the color
    is inherited by all children that don't set their own text-* utility.

    "white" and "transparent" are offered by the Background mixin but are
    not theme colors, so no helper class is compiled for them.
    """
    if not background_context or background_context == "transparent":
        return ""
    if background_context == "white":
        return "text-body"
    return f"text-bg-{background_context}"


@register.filter
def filter_by_type(plugins, plugin_types):
    """Filter plugins by type(s)
    Usage: plugins|filter_by_type:"CounterPlugin,ImagePlugin"
    """
    if isinstance(plugin_types, str):
        plugin_types = [t.strip() for t in plugin_types.split(',')]
    return [p for p in plugins if p.plugin_type in plugin_types]


@register.simple_tag
def get_clip_path_data(clip_path_id):
    """Return clip path config for the given id, or None if not found / id is 'none'.

    The returned dict includes the original view_width, view_height, path keys
    plus computed scale_x and scale_y values for use in an SVG
    clipPathUnits="objectBoundingBox" transform.
    """
    if not clip_path_id or clip_path_id == "none":
        return None
    clip_paths = getattr(settings, "CMS_HERO_CLIP_PATHS", [])
    for entry in clip_paths:
        if entry[0] == clip_path_id and len(entry) > 2 and entry[2] is not None:
            data = dict(entry[2])
            data["scale_x"] = round(1.0 / data["view_width"], 8)
            data["scale_y"] = round(1.0 / data["view_height"], 8)
            return data
    return None

@register.filter
def to_nocookie_embed(url):
    """Rewrite YouTube embed URLs to the privacy-enhanced youtube-nocookie.com domain.

    Why: Safari's Intelligent Tracking Prevention blocks third-party requests
    to youtube.com (stats/log endpoints), causing the embedded player to fail
    with error 153. youtube-nocookie.com is exempted because it doesn't set
    cookies until the user interacts with the player.
    """
    if not url:
        return url
    return url.replace("://www.youtube.com/embed/", "://www.youtube-nocookie.com/embed/").replace(
        "://youtube.com/embed/", "://www.youtube-nocookie.com/embed/"
    )


@register.filter
def get_slot(instance, slot_name):
    """Get plugins for a specific slot
    Usage: plugins|get_slot:"community"
    """
    plugin_type = f"{instance.__class__.__name__}{slot_name.capitalize()}Plugin"
    for plugin in instance.child_plugin_instances:
        if plugin.plugin_type == plugin_type:
            yield from plugin.child_plugin_instances


#: Icon class tokens that describe the *style* of an icon rather than the icon
#: itself, and so carry no meaning for an accessible name.
ICON_STYLE_CLASSES = frozenset(
    (
        "fa", "fas", "far", "fal", "fat", "fab", "fad",
        "fa-solid", "fa-regular", "fa-light", "fa-thin", "fa-duotone",
        "fa-brands", "fa-classic", "fa-sharp", "fa-fw",
        "bi",
    )
)

#: Icon slugs whose title-cased form reads wrong.
ICON_LABEL_OVERRIDES = {
    "x-twitter": "X",
    "square-x-twitter": "X",
    "github": "GitHub",
    "gitlab": "GitLab",
    "linkedin": "LinkedIn",
    "linkedin-in": "LinkedIn",
    "youtube": "YouTube",
    "stack-overflow": "Stack Overflow",
    "discord": "Discord",
    "mastodon": "Mastodon",
    "bluesky": "Bluesky",
    "rss": "RSS",
}


@register.filter
def icon_link_label(instance):
    """Return an accessible name for a link whose only content is an icon.

    An icon-only link renders as <a><i class="fa-brands fa-mastodon"></i></a>,
    which has no accessible name at all (WCAG 2.4.4 / axe "link-name"). The
    footer social row is built this way, so the failure repeats on every page.

    Returns an empty string — meaning "nothing to add" — whenever the link
    already has a name: link text, child plugins that render the text, or an
    aria-label/aria-labelledby/title the editor set by hand. Otherwise the
    name is derived from the icon class, so fa-brands fa-mastodon yields
    "Mastodon".
    """
    if instance.config.get("name", ""):
        return ""
    if getattr(instance, "child_plugin_instances", None):
        return ""
    attributes = instance.config.get("attributes") or {}
    if any(attributes.get(key) for key in ("aria-label", "aria-labelledby", "title")):
        return ""

    for icon in (instance.config.get("icon_left"), instance.config.get("icon_right")):
        if not icon:
            continue
        classes = icon.get("iconClass", "") if isinstance(icon, dict) else str(icon)
        for token in classes.split():
            if token in ICON_STYLE_CLASSES:
                continue
            slug = token.split("-", 1)[1] if "-" in token else token
            if not slug:
                continue
            return ICON_LABEL_OVERRIDES.get(slug, slug.replace("-", " ").title())
    return ""


@register.filter
def card_link_label(instance):
    """Return an accessible name for a card's stretched link.

    A linked card renders an empty ``<a class="stretched-link"></a>`` over the
    whole card, which has no accessible name at all (WCAG 2.4.4 / axe
    "link-name"). The card title is what a sighted user reads before clicking,
    so it is the right name; a card without a title falls back to the opening
    words of its body text.
    """
    title = strip_tags(instance.config.get("card_title") or "").strip()
    if title:
        return title
    content = strip_tags(instance.config.get("card_content") or "").strip()
    return Truncator(content).words(8) if content else ""


@register.filter
def image_link_label(instance):
    """Return an accessible name for an Image plugin that is wrapped in a link.

    A link whose only content is an image takes its name from that image's alt
    text, so an image left with ``alt=""`` makes the link nameless. Editors do
    not always fill in the alt text, and the clipped templates render an SVG
    that carries no alt text at all, so fall back to what filer knows about the
    file: its alt text, then its label (its name, or failing that the uploaded
    filename).

    A filename is a poor name and the real fix is for an editor to set the alt
    text, but it keeps the link reachable for screen reader and voice control
    users in the meantime.
    """
    alt = (instance.config.get("attributes") or {}).get("alt")
    if alt:
        return alt
    image = getattr(instance, "rel_image", None)
    if image is None:
        return ""
    return (image.default_alt_text or "").strip() or image.label or ""


@register.simple_tag
def capped_image(instance, max_width=1600):
    """Resolve a djangocms-frontend Image plugin to a {url, width} pair.

    Image.img_src only runs the file through easy-thumbnails when the editor
    gave the plugin a width, a height or a thumbnail option; with none of those
    it hands back rel_image.url, i.e. the untouched upload. That is how single
    pages ended up carrying megabytes of images.

    Thumbnailing an unsized image at max_width with upscale=False leaves small
    images at their own dimensions while still converting them to WebP, so the
    re-encode is worth it even when there is nothing to downscale.

    Returns the width alongside the URL because callers put it in a srcset
    descriptor: advertising the capped file under the *original* width would
    make the browser pick it for viewports it cannot actually fill.

    Falls back to img_src whenever thumbnailing cannot apply: external URLs,
    missing files, and SVGs (filer stores those as Image, but easy-thumbnails
    has no source generator for them and raises).
    """
    from easy_thumbnails.exceptions import InvalidImageFormatError
    from easy_thumbnails.files import get_thumbnailer

    def uncapped():
        try:
            width = instance.get_size()["size"][0]
        except Exception:
            width = getattr(instance.rel_image, "width", 0) if instance.rel_image else 0
        return {"url": instance.img_src, "width": width}

    if getattr(instance, "external_picture", None):
        return uncapped()
    image = getattr(instance, "rel_image", None)
    if not image:
        return uncapped()
    if instance.config.get("width") or instance.config.get("height") or instance.config.get("thumbnail_options"):
        return uncapped()

    try:
        thumb = get_thumbnailer(image).get_thumbnail(
            {
                "size": (max_width, 0),
                "crop": False,
                "upscale": False,
                "subject_location": image.subject_location,
            }
        )
        return {"url": thumb.url, "width": thumb.width}
    except (InvalidImageFormatError, OSError, ValueError, AttributeError):
        return uncapped()


@register.filter
def thumb_or_original(thumbnail, original):
    """Fall back to the original file when a {% thumbnail %} call came back empty.

    easy-thumbnails' template tag swallows errors unless THUMBNAIL_DEBUG is on
    and leaves the target variable empty, which would render src="". SVG uploads
    hit this on every template that thumbnails a filer image.
    """
    if thumbnail:
        return thumbnail.url
    return original.url if original else ""
