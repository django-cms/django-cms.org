from django import forms
from django.utils.translation import gettext_lazy as _
from djangocms_frontend import settings as frontend_settings
from djangocms_frontend.component_base import CMSFrontendComponent
from djangocms_frontend.component_pool import components
from djangocms_frontend.fields import ColoredButtonGroup

from .models import Member, MembershipType


def _get_member_queryset(config, *, require_logo=False):
    """Shared queryset builder for member plugins."""
    qs = Member.objects.all()
    if require_logo:
        qs = qs.exclude(logo__isnull=True)
    membership_types = config.get("membership_types")
    if membership_types:
        qs = qs.filter(membership_type__in=membership_types)
    max_items = config.get("max_items")
    if max_items:
        qs = qs[:max_items]
    return qs


@components.register
class MemberCards(CMSFrontendComponent):
    """Member cards grid section"""

    class Meta:
        name = _("Member Cards")
        render_template = "members/member_cards.html"
        allow_children = False
        mixins = ["Background", "Spacing", "Attributes"]

    heading = forms.CharField(
        label=_("Heading"),
        required=False,
    )

    eyebrow_text = forms.CharField(
        label=_("Eyebrow text"),
        required=False,
    )

    membership_types = forms.MultipleChoiceField(
        label=_("Filter by membership type"),
        choices=MembershipType.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text=_("Select one or more types to filter. Leave empty to show all."),
    )

    max_items = forms.IntegerField(
        label=_("Maximum members displayed"),
        required=False,
        min_value=1,
        help_text=_("Limit the number of members shown. Leave empty for no limit."),
    )

    text_color = forms.ChoiceField(
        label=_("Text color"),
        choices=frontend_settings.EMPTY_CHOICE + frontend_settings.COLOR_STYLE_CHOICES,
        initial=frontend_settings.EMPTY_CHOICE[0][0],
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
        required=False,
    )

    def get_short_description(self):
        return self.config.get("heading", "")

    def get_members(self):
        return _get_member_queryset(self.config)


@components.register
class MemberCarousel(CMSFrontendComponent):
    """Member logos carousel using Swiper"""

    class Meta:
        name = _("Member Carousel")
        render_template = "members/member_carousel.html"
        allow_children = False
        mixins = ["Background", "Spacing", "Attributes"]

    heading = forms.CharField(
        label=_("Heading"),
        required=False,
    )

    membership_types = forms.MultipleChoiceField(
        label=_("Filter by membership type"),
        choices=MembershipType.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text=_("Select one or more types to filter. Leave empty to show all."),
    )

    max_items = forms.IntegerField(
        label=_("Maximum members displayed"),
        required=False,
        min_value=1,
        help_text=_("Limit the number of members shown. Leave empty for no limit."),
    )

    text_color = forms.ChoiceField(
        label=_("Text color"),
        choices=frontend_settings.EMPTY_CHOICE + frontend_settings.COLOR_STYLE_CHOICES,
        initial=frontend_settings.EMPTY_CHOICE[0][0],
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
        required=False,
    )

    bg_color = forms.ChoiceField(
        label=_("Background color"),
        choices=frontend_settings.EMPTY_CHOICE + frontend_settings.COLOR_STYLE_CHOICES,
        initial=frontend_settings.EMPTY_CHOICE[0][0],
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
        required=False,
    )

    loop = forms.BooleanField(
        label=_("Loop"),
        required=False,
        initial=True,
    )

    autoplay = forms.BooleanField(
        label=_("Autoplay"),
        required=False,
        initial=True,
    )

    delay = forms.IntegerField(
        label=_("Autoplay delay (ms)"),
        required=False,
        initial=3000,
    )

    btn_color = forms.ChoiceField(
        label=_("Button color"),
        choices=frontend_settings.COLOR_STYLE_CHOICES,
        required=False,
        initial="primary",
        widget=ColoredButtonGroup(attrs={"class": "flex-wrap"}),
    )

    def get_short_description(self):
        return self.config.get("heading", "")

    def get_members(self):
        return _get_member_queryset(self.config, require_logo=True)
