from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from djangocms_frontend.component_base import CMSFrontendComponent
from djangocms_frontend.component_pool import components
from djangocms_frontend.fields import ColoredButtonGroup


@components.register
class Hero(CMSFrontendComponent):
    """Hero component with background grid option"""

    class Meta:
        name = _("Hero")
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


# Timeline
@components.register
class TimelineContainer(CMSFrontendComponent):
    """Timeline component with vertical layout option"""

    class Meta:
        name = _("Timeline")
        render_template = "timeline/timeline.html"
        allow_children = True
        child_classes = [
            "CardPlugin",
            "TextPlugin",
            "HeadingPlugin",
            "SpacingPlugin",
        ]
        mixins = [
            "Background",
            "Spacing",
            "Attributes",
        ]

    background_grid = forms.BooleanField(
        label=_("Show background grid"),
        required=False,
        initial=False,
    )

    divider_color = forms.ChoiceField(
        label=_("Divider line color"),
        choices=settings.DJANGOCMS_FRONTEND_COLOR_STYLE_CHOICES,
        required=False,
        initial="primary",
        help_text=_("Color of the vertical timeline line."),
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
    )

    circle_color = forms.ChoiceField(
        label=_("Circle color"),
        choices=settings.DJANGOCMS_FRONTEND_COLOR_STYLE_CHOICES,
        required=False,
        initial="secondary",
        help_text=_("Color of the timeline circles."),
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
    )
