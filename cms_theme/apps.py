from django.apps import AppConfig


class CmsThemeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cms_theme"

    def ready(self) -> None:
        from djangocms_frontend.contrib.content.cms_plugins import CodeBlockPlugin
        from djangocms_frontend.contrib.grid.cms_plugins import GridColumnPlugin

        CodeBlockPlugin.change_form_template = "code_block/admin/code_block.html"
        GridColumnPlugin.is_slot = True
