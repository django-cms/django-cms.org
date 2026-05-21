from django.apps import AppConfig


class CmsThemeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cms_theme"

    root_plugins = ("TextPlugin", "MDTextPlugin", "Alias")

    def ready(self) -> None:
        from cms.plugin_pool import plugin_pool
        from djangocms_frontend.contrib.grid.cms_plugins import GridColumnPlugin

        GridColumnPlugin.is_slot = True

        plugin_pool.discover_plugins()
        for plugin_type, plugin in plugin_pool.plugins.items():
            if plugin_type not in self.root_plugins and str(plugin.module) != "Sections" and plugin.allowed_models is None:
                plugin.require_parent = True
