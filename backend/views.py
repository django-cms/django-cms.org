from django.db.models import Q

from djangocms_stories.views import (
    AuthorEntriesView,
    CategoryEntriesView,
    PostArchiveView,
    PostListView,
    TaggedListView,
)


class OptimizedListMixin:
    """Extend the library's list-view query optimization for our templates.

    The base ``optimize()`` only covers ``post__app_config`` and
    ``post__categories``. Our blog list templates additionally render, per post,
    the main image (``post_item.html`` / ``card_image_top.html``) and the author
    profile with its photo (``card_author.html``). Pulling those in avoids an
    N+1 query per post in the list. All paths are nullable FKs / a reverse
    OneToOne, so select_related uses LEFT JOINs.
    """

    def optimize(self, qs):
        return super().optimize(qs).select_related(
            "post__main_image",
            "post__author",
            "post__author__author_profile",
            "post__author__author_profile__photo",
        )


class SearchPostListView(OptimizedListMixin, PostListView):
    """Extends PostListView with ?q= search filtering on title and abstract."""

    def get_queryset(self):
        qs = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        if query:
            qs = qs.filter(
                Q(title__icontains=query) | Q(abstract__icontains=query)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "").strip()
        return context


class OptimizedPostArchiveView(OptimizedListMixin, PostArchiveView):
    pass


class OptimizedTaggedListView(OptimizedListMixin, TaggedListView):
    pass


class OptimizedAuthorEntriesView(OptimizedListMixin, AuthorEntriesView):
    pass


class OptimizedCategoryEntriesView(OptimizedListMixin, CategoryEntriesView):
    pass
