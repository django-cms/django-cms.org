from django.apps import AppConfig


class CmsThemeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cms_theme"

    def ready(self) -> None:
        from cms.plugin_pool import plugin_pool

        code_plugin = plugin_pool.get_plugin("CodeBlockPlugin")
        if code_plugin:
            code_plugin.change_form_template = "code_block/admin/code_block.html"
            