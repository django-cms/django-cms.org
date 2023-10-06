from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _
from djangocms_frontend.cms_plugins import CMSUIPlugin
from djangocms_frontend.common.responsive import ResponsiveMixin
from djangocms_frontend.common.spacing import MarginMixin

from . import forms, models


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
                    "template",
                ]
            },
        ),
    ]

    @staticmethod
    def get_render_template(context, instance, placeholder):
        return f"cms_theme/person/{instance.template}/person.html"


@plugin_pool.register_plugin
class FeaturePlugin(ResponsiveMixin, MarginMixin, CMSUIPlugin):
    name = _("Feature")

    model = models.Feature
    form = forms.FeatureForm

    allow_children = True

    render_template = "cms_theme/feature.html"

    fieldsets = [
        (
            None,
            {
                "fields": [
                    ("icon", "feature"),
                ]
            },
        ),
    ]


@plugin_pool.register_plugin
class CaseStudyProfilePlugin(CMSUIPlugin):
    name = _("Case study profile")

    model = models.CaseStudyProfile
    form = forms.CaseStudyProfileForm

    render_template = "cms_theme/case_study_profile.html"

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
    ]
