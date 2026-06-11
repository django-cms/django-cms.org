from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.utils.translation import get_language

from cms.sitemaps import CMSSitemap

from djangocms_stories.models import PostContent


class StorySitemap(Sitemap):
    """Sitemap for published djangocms-stories posts."""

    changefreq = "weekly"
    priority = 0.5
    protocol = settings.META_SITE_PROTOCOL

    def items(self):
        # ``PostContent.objects`` is the versioning manager and only returns
        # published content. Skip posts whose URL cannot be resolved (e.g.
        # missing slug or category) so the sitemap never lists empty locations.
        contents = (
            PostContent.objects.filter(language=get_language())
            .select_related("post", "post__app_config")
        )
        return [content for content in contents if content.get_absolute_url()]

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return obj.post.date_modified


sitemaps = {
    "cmspages": CMSSitemap,
    "stories": StorySitemap,
}
