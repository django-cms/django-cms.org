from django.apps import AppConfig


class CmsThemeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cms_theme"

    def ready(self) -> None:
        from djangocms_frontend.contrib.grid.cms_plugins import GridColumnPlugin

        GridColumnPlugin.is_slot = True
