from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _
from djangocms_frontend.cms_plugins import CMSUIPlugin
from djangocms_frontend.common.responsive import ResponsiveMixin
from djangocms_frontend.common.spacing import MarginMixin
from djangocms_frontend.contrib.link.cms_plugins import LinkPluginMixin
from djangocms_frontend.helpers import first_choice

from . import forms, models
from . import conf


def get_plugin_template(
    instance: models.FrontendUIItem, plugin: str, template: str, templates: tuple
) -> str:
    layout = getattr(instance, "template", first_choice(templates))
    return f"cms_theme/{plugin}/{layout}/{template}.html"


@plugin_pool.register_plugin
class PersonPlugin(ResponsiveMixin, MarginMixin, CMSUIPlugin):
    name = _("Person")

    model = models.Person
    form = forms.PersonForm

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
                ]
            }
        ),
    ]

    @staticmethod
    def get_render_template(context, instance, placeholder):
        return get_plugin_template(instance, "person", "person", conf.PERSON_LAYOUTS)


@plugin_pool.register_plugin
class FeaturePlugin(ResponsiveMixin, MarginMixin, CMSUIPlugin):
    name = _("Feature")

    model = models.Feature
    form = forms.FeatureForm

    allow_children = True
    child_classes = [
        "ImagePlugin",
        "IconPlugin",
    ]

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

    def get_render_template(self, context, instance, placeholder):
        return get_plugin_template(
            instance,
            "feature",
            "feature",
            conf.FEATURE_LAYOUTS,
        )


@plugin_pool.register_plugin
class CaseStudyProfilePlugin(CMSUIPlugin):
    name = _("Case study profile")

    model = models.CaseStudyProfile
    form = forms.CaseStudyProfileForm

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

    def get_render_template(self, context, instance, placeholder):
        return get_plugin_template(
            instance,
            "case_study",
            "case_study",
            conf.CASE_STUDY_LAYOUTS,
        )


@plugin_pool.register_plugin
class PromoCardPlugin(ResponsiveMixin, MarginMixin, LinkPluginMixin, CMSUIPlugin):
    name = _("Promo card")

    model = models.PromoCard
    form = forms.PromoCardForm

    allow_children = True

    fieldsets = [
        (
            None,
            {
                "fields": [
                    "image",
                    "icon",
                    "title",
                    "subtitle",
                ]
            },
        ),
        (
            _("Layout"),
            {
                "classes": ("collapse",),
                "fields": [
                    "template",
                ]
            }
        ),
    ]
    link_fieldset_position = 1

    def get_render_template(self, context, instance, placeholder):
        return get_plugin_template(
            instance,
            "promo",
            "promo",
            conf.PROMO_LAYOUTS,
        )
