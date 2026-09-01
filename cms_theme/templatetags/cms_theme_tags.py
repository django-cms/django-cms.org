from django import template
from django.conf import settings

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
