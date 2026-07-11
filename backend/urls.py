from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView

from cms.sitemaps import CMSSitemap
from djangocms_stories.sitemaps import StoriesSitemap

sitemaps = {
    "cmspages": CMSSitemap,
    "stories": StoriesSitemap,
}

urlpatterns = [
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="robots.txt",
            content_type="text/plain",
            extra_context={"allow_indexing": settings.ROBOTS_ALLOW_INDEXING},
        ),
    ),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))

urlpatterns.append(path("", include("cms.urls")))

# the new django admin sidebar is bad UX in django CMS custom admin views.
admin.site.enable_nav_sidebar = False
