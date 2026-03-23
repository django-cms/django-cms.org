from django import forms
from django.utils.translation import gettext_lazy as _
from djangocms_frontend import settings as frontend_settings
from djangocms_frontend.component_base import CMSFrontendComponent
from djangocms_frontend.component_pool import components
from djangocms_frontend.fields import ColoredButtonGroup

from .models import Member, MembershipType


class MemberChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.name} ({obj.get_membership_type_display()})"


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

    membership_type = forms.ChoiceField(
        label=_("Filter by membership type"),
        choices=[("", _("All"))] + MembershipType.choices,
        required=False,
        help_text=_("Only show members of this type. Leave empty to show all."),
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
        qs = Member.objects.all()
        membership_type = self.config.get("membership_type")
        if membership_type:
            qs = qs.filter(membership_type=membership_type)
        return qs


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

    membership_type = forms.ChoiceField(
        label=_("Filter by membership type"),
        choices=[("", _("All"))] + MembershipType.choices,
        required=False,
        help_text=_("Only show members of this type. Leave empty to show all."),
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
        qs = Member.objects.exclude(logo__isnull=True)
        membership_type = self.config.get("membership_type")
        if membership_type:
            qs = qs.filter(membership_type=membership_type)
        return qs
