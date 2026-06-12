from django import forms
from django.db.models import ManyToOneRel
from django.utils.translation import gettext_lazy as _
from djangocms_frontend.common import (
    MarginFormMixin,
    ResponsiveFormMixin,
)
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
