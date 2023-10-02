from django import forms
from django.conf import settings as django_settings
from django.db.models import ManyToOneRel
from django.utils.translation import gettext_lazy as _
from djangocms_frontend.common.responsive import ResponsiveFormMixin
from djangocms_frontend.common.spacing import MarginFormMixin
from djangocms_frontend.contrib.icon.fields import IconPickerField
from djangocms_frontend.helpers import first_choice
from djangocms_frontend.models import FrontendUIItem
from entangled.forms import EntangledModelForm
from filer.fields.image import AdminImageFormField, FilerImageField
from filer.models import Image


def get_templates(settings_name):
    """Add additional choices through the ``settings.py``."""
    choices = getattr(
        django_settings,
        settings_name,
        [
            ("default", _("Default")),
        ],
    )
    return choices


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
        label=_("Template"),
        choices=get_templates("PERSON_TEMPLATES"),
        initial=first_choice(get_templates("PERSON_TEMPLATES")),
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
