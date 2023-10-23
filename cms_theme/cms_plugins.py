from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _
from djangocms_frontend.cms_plugins import CMSUIPlugin
from djangocms_frontend.common.responsive import ResponsiveMixin
from djangocms_frontend.common.spacing import MarginMixin
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


@plugin_pool.register_plugin
class FeaturePlugin(LayoutMixin, ResponsiveMixin, MarginMixin, CMSUIPlugin):
    name = _("Feature")

    model = models.Feature
    form = forms.FeatureForm

    allow_children = True
    child_classes = [
        "ImagePlugin",
        "IconPlugin",
    ]

    layout_tuple = ("feature", "feature")

    fieldsets = [
        (
            None,
            {
                "fields": [
                    ("icon", "feature"),
                    "template",
                ]
            },
        ),
    ]


@plugin_pool.register_plugin
class CaseStudyProfilePlugin(LayoutMixin, CMSUIPlugin):
    name = _("Case study profile")

    model = models.CaseStudyProfile
    form = forms.CaseStudyProfileForm

    layout_tuple = ("case_study", "case_study")

    fieldsets = [
        (
            None,
            {
                "fields": [
                    "client",
                    "size",
                    "location",
                    "sector",
                    "launch",
                    "website",
                    "source",
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


@plugin_pool.register_plugin
class PromoCardPlugin(LayoutMixin, MarginMixin, LinkPluginMixin, CMSUIPlugin):
    name = _("Promo card")

    model = models.PromoCard
    form = forms.PromoCardForm

    allow_children = True

    layout_tuple = ("promo", "promo")

    fieldsets = [
        (
            None,
            {
                "fields": [
                    "title",
                    "subtitle",
                    "image",
                    "icon",
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
    link_fieldset_position = 1
