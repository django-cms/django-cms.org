from django.urls import path

from djangocms_stories.urls import urlpatterns as stories_urlpatterns

from .views import SearchPostListView

app_name = "djangocms_stories"

# Start with our search-enabled list view
urlpatterns = [
    path("", SearchPostListView.as_view(), name="posts-latest"),
]

# Add all other original URL patterns (skip the original posts-latest)
urlpatterns += [p for p in stories_urlpatterns if p.name != "posts-latest"]
