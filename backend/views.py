from django.db.models import Q

from djangocms_stories.views import PostListView


class SearchPostListView(PostListView):
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
