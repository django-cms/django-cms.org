from django.urls import path

from djangocms_stories.urls import urlpatterns as stories_urlpatterns

from .views import (
    OptimizedAuthorEntriesView,
    OptimizedCategoryEntriesView,
    OptimizedPostArchiveView,
    OptimizedTaggedListView,
    SearchPostListView,
)

app_name = "djangocms_stories"

# List routes we replace with query-optimized subclasses (see OptimizedListMixin).
_optimized = {
    "posts-latest": SearchPostListView,
    "posts-category": OptimizedCategoryEntriesView,
    "posts-archive": OptimizedPostArchiveView,
    "posts-author": OptimizedAuthorEntriesView,
    "posts-tagged": OptimizedTaggedListView,
}

urlpatterns = []
for p in stories_urlpatterns:
    view = _optimized.get(p.name)
    if view is not None:
        urlpatterns.append(path(str(p.pattern), view.as_view(), name=p.name))
    else:
        urlpatterns.append(p)
