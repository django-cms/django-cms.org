from django.apps import AppConfig


class CmsThemeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cms_theme"

    def ready(self):
        from djangocms_frontend.contrib.utilities.cms_plugins import HeadingPlugin

        HeadingPlugin.is_local = True
