from django import forms
from django.utils.translation import gettext_lazy as _
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

@components.register
class LogoCarousel(CMSFrontendComponent):
    """LogoCarousel component"""

    class Meta:
        name = _("Logo Carousel")
        render_template = "carousel/logo_carousel.html"
        allow_children = True
        child_classes = [
                "CarouselItemPlugin",
        ]
        mixins = ["Background", "Spacing", "Attributes"]


    title = forms.CharField(
            label=_("Title"),
            required=False,
    )

    loop = forms.BooleanField(
            label=_("Loop Carousel"),
            required=False,
            initial=False,
    )
    space_between_slides = forms.IntegerField(
            label=_("Space Between Slides"),
            required=False,
            initial=20,
    )
    autoplay = forms.BooleanField(
            label=_("AutoPlay"),
            required=False,
            initial=True,
    )
    delay = forms.IntegerField(
            label=_("Autoplay delay"),
            required=False,
            initial=3000,
    )
