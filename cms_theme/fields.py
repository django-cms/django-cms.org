from django import forms
from django.conf import settings
from djangocms_frontend.fields import ColoredButtonGroup


class ColorChoiceField(forms.ChoiceField):
    """ChoiceField with ColoredButtonGroup widget, using choices from DJANGOCMS_FRONTEND_COLOR_STYLE_CHOICES."""

    def __init__(self, *args, **kwargs):
        choices = (("", "---------"),) + tuple(
            settings.DJANGOCMS_FRONTEND_COLOR_STYLE_CHOICES
        )
        kwargs.setdefault("choices", choices)
        kwargs.setdefault("widget", ColoredButtonGroup())
        kwargs.setdefault("required", False)
        super().__init__(*args, **kwargs)
