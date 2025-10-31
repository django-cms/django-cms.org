from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _
from djangocms_frontend.cms_plugins import CMSUIPlugin
from djangocms_frontend.common import ResponsiveMixin
from djangocms_frontend.common import MarginMixin
from djangocms_frontend.contrib.link.cms_plugins import LinkPluginMixin
from djangocms_frontend.helpers import first_choice

from . import forms, models


class LayoutMixin:
    def get_render_template(self, context, instance, placeholder):
        layout = getattr(instance, "template", first_choice(self.form.LAYOUTS))
        plugin, template = self.layout_tuple
        return f"cms_theme/{plugin}/{layout}/{template}.html"


@plugin_pool.register_plugin
class PersonPlugin(LayoutMixin, ResponsiveMixin, MarginMixin, CMSUIPlugin):
    name = _("Person")

    model = models.Person
    form = forms.PersonForm

    layout_tuple = ("person", "person")

    fieldsets = [
        (
            None,
            {
                "fields": [
                    "picture",
                    "name",
                    "role",
                ]
            },
        ),
        (
            _("Layout"),
            {
                "classes": ("collapse",),
                "fields": [
                    "template",
                ],
            },
        ),
    ]
