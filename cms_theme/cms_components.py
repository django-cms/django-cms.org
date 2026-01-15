from django import forms
from django.utils.translation import gettext_lazy as _
from djangocms_frontend.common import (
    AttributesMixin,
    BackgroundMixin,
    SpacingMixin,
)
from djangocms_frontend.component_base import CMSFrontendComponent
from djangocms_frontend.component_pool import components


@components.register
class Hero(CMSFrontendComponent):
    """Hero component with background grid option"""

    class Meta:
        plugin_name = _("Hero")
        render_template = "hero/hero.html"
        allow_children = True
        child_classes = [
            "TextPlugin",
            "TextLinkPlugin",
            "ImagePlugin",
            "HeadingPlugin",
            "CounterPlugin",
        ]
        mixins = ["Background", "Spacing", "Attributes"]

    background_grid = forms.BooleanField(
        label=_("Show background grid"),
        required=False,
        initial=False,
    )
