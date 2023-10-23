from django import forms
from django.conf import settings as django_settings
from django.db.models import ManyToOneRel
from django.utils.translation import gettext_lazy as _
from djangocms_frontend.common.responsive import ResponsiveFormMixin
from djangocms_frontend.common.spacing import MarginFormMixin
from djangocms_frontend.contrib.icon.fields import IconPickerField
from djangocms_frontend.contrib.link.forms import AbstractLinkForm
from djangocms_frontend.helpers import first_choice
from djangocms_frontend.models import FrontendUIItem
from djangocms_text_ckeditor.fields import HTMLFormField
from entangled.forms import EntangledModelForm
from filer.fields.image import AdminImageFormField, FilerImageField
from filer.models import Image

from . import conf


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

    template = forms.ChoiceField(
        label=_("Layout"),
        choices=conf.PERSON_LAYOUTS,
        initial=first_choice(conf.PERSON_LAYOUTS),
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
        choices=conf.FEATURE_LAYOUTS,
        initial=first_choice(conf.FEATURE_LAYOUTS),
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
        choices=conf.CASE_STUDY_LAYOUTS,
        initial=first_choice(conf.CASE_STUDY_LAYOUTS),
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
        choices=conf.CASE_STUDY_LAYOUTS,
        initial=first_choice(conf.CASE_STUDY_LAYOUTS),
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
            ],
        }

    link_is_optional = True

    template = forms.ChoiceField(
        label=_("Layout"),
        choices=conf.PERSON_LAYOUTS,
        initial=first_choice(conf.PERSON_LAYOUTS),
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
