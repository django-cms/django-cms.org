from django import forms
from django.db.models import ManyToOneRel
from django.utils.translation import gettext_lazy as _
from djangocms_frontend.common import ResponsiveFormMixin
from djangocms_frontend.common import MarginFormMixin
from djangocms_frontend.contrib.icon.fields import IconPickerField
from djangocms_frontend.contrib.link.forms import AbstractLinkForm
from djangocms_frontend.helpers import first_choice
from djangocms_frontend.models import FrontendUIItem
from djangocms_text_ckeditor.fields import HTMLFormField
from entangled.forms import EntangledModelForm
from filer.fields.image import AdminImageFormField, FilerImageField
from filer.models import Image


class PersonForm(
    ResponsiveFormMixin,
    MarginFormMixin,
    EntangledModelForm,
):
    class Meta:
        model = FrontendUIItem
        entangled_fields = {
            "config": [
                "template",
                "picture",
                "name",
                "role",
            ],
        }

    LAYOUTS = (("default", _("Default")),)

    template = forms.ChoiceField(
        label=_("Layout"),
        choices=LAYOUTS,
        initial=first_choice(LAYOUTS),
    )

    picture = AdminImageFormField(
        rel=ManyToOneRel(FilerImageField, Image, "id"),
        queryset=Image.objects.all(),
        to_field_name="id",
        label=_("Image"),
        required=False,
    )

    name = forms.CharField(
        label=_("Name"),
        required=True,
    )

    role = forms.CharField(
        label=_("Role"),
        required=False,
    )


class FeatureForm(ResponsiveFormMixin, MarginFormMixin, EntangledModelForm):
    class Meta:
        model = FrontendUIItem
        entangled_fields = {
            "config": [
                "icon",
                "feature",
                "template",
            ]
        }

    LAYOUTS = (("default", _("Default")),)

    icon = IconPickerField(
        label=_("Icon"),
        required=True,
    )
    feature = forms.CharField(
        label=_("Feature"),
        required=True,
        widget=forms.Textarea,
    )
    template = forms.ChoiceField(
        label=_("Layout"),
        choices=LAYOUTS,
        initial=first_choice(LAYOUTS),
    )


class CaseStudyProfileForm(EntangledModelForm):
    class Meta:
        model = FrontendUIItem
        entangled_fields = {
            "config": [
                "client",
                "size",
                "location",
                "sector",
                "launch",
                "website",
                "source",
                "template",
            ]
        }

    LAYOUTS = (("default", _("Default")),)

    client = forms.CharField(
        label=_("Client"),
        required=True,
    )
    size = forms.CharField(
        label=_("Size"),
        required=False,
    )
    location = forms.CharField(
        label=_("Location"),
        required=False,
    )
    sector = forms.CharField(
        label=_("Sector"),
        required=False,
    )
    launch = forms.IntegerField(
        label=_("Year of launch"),
        required=False,
    )
    website = forms.URLField(
        label=_("Website"),
        required=False,
    )
    source = HTMLFormField(
        label=_("Source"),
        required=False,
        help_text=_("Creator of the case study"),
    )
    template = forms.ChoiceField(
        label=_("Layout"),
        choices=LAYOUTS,
        initial=first_choice(LAYOUTS),
    )


class CaseStudyProfileForm(EntangledModelForm):
    class Meta:
        model = FrontendUIItem
        entangled_fields = {
            "config": [
                "client",
                "size",
                "location",
                "sector",
                "launch",
                "website",
                "source",
                "template",
            ]
        }

    LAYOUTS = (("default", _("Default")),)

    client = forms.CharField(
        label=_("Client"),
        required=True,
    )
    size = forms.CharField(
        label=_("Size"),
        required=False,
    )
    location = forms.CharField(
        label=_("Location"),
        required=False,
    )
    sector = forms.CharField(
        label=_("Sector"),
        required=False,
    )
    launch = forms.IntegerField(
        label=_("Year of launch"),
        required=False,
    )
    website = forms.URLField(
        label=_("Website"),
        required=False,
    )
    source = HTMLFormField(
        label=_("Source"),
        required=False,
        help_text=_("Creator of the case study"),
    )
    template = forms.ChoiceField(
        label=_("Layout"),
        choices=LAYOUTS,
        initial=first_choice(LAYOUTS),
    )


class PromoCardForm(
    ResponsiveFormMixin,
    MarginFormMixin,
    AbstractLinkForm,
):
    class Meta:
        model = FrontendUIItem
        entangled_fields = {
            "config": [
                "template",
                "title",
                "subtitle",
                "icon",
                "image",
            ],
        }

    LAYOUTS = (("default", _("Default")),)

    link_is_optional = True

    template = forms.ChoiceField(
        label=_("Layout"),
        choices=LAYOUTS,
        initial=first_choice(LAYOUTS),
    )

    image = AdminImageFormField(
        rel=ManyToOneRel(FilerImageField, Image, "id"),
        queryset=Image.objects.all(),
        to_field_name="id",
        label=_("Image"),
        required=False,
    )
    icon = IconPickerField(
        label=_("Icon"),
        required=False,
    )
    title = forms.CharField(
        label=_("Title"),
        required=True,
    )
    subtitle = forms.CharField(
        label=_("Subtitle"),
        required=False,
    )
