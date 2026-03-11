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
