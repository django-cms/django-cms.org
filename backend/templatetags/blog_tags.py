from django import template
from django.db.models import Q
from django.db.models.functions import Coalesce
from django.utils.timezone import now
from djangocms_stories.models import PostCategory, PostContent
from cms.utils import get_current_site

register = template.Library()


@register.simple_tag
def get_blog_categories():
    return PostCategory.objects.order_by("priority", "translations__name")


@register.simple_tag(takes_context=True)
def page_url(context, page_number):
    """Build a pagination URL preserving existing GET parameters."""
    request = context["request"]
    params = request.GET.copy()
    params[context.get("view").page_kwarg] = page_number
    return "?{}".format(params.urlencode())


@register.simple_tag
def pagination_range(current_page, total_pages, neighbours=1):
    """Return list of page numbers/ellipsis for pagination.

    Always shows first, last, and `neighbours` pages around current.
    Example with current=3, total=7, neighbours=1: [1, 2, 3, 4, '...', 7]
    """
    if total_pages <= 1:
        return []

    pages = set()
    pages.add(1)
    pages.add(total_pages)
    for i in range(current_page - neighbours, current_page + neighbours + 1):
        if 1 <= i <= total_pages:
            pages.add(i)

    result = []
    for page in sorted(pages):
        if result and page - result[-1] > 1:
            result.append("...")
        result.append(page)
    return result


@register.filter
def est_read_time(post_content):
    return 5


@register.simple_tag(name="adjacent_post_urls", takes_context=True)
def adjacent_post_urls(context, post_content):
    """
    Returns a dict with previous_url and next_url for the given PostContent.
    previous_url = newer post in list order
    next_url = older post in list order
    """
    if not post_content:
        return {"previous_url": "", "next_url": ""}

    request = context.get("request")
    if request is None:
        return {"previous_url": "", "next_url": ""}

    ts = now()
    current = post_content
    current_sort_date = current.post.date_published or current.post.date_created

    base = (
        PostContent.objects
        .filter(
            language=current.language,
            post__app_config=current.post.app_config,
        )
        .on_site(get_current_site(request))
        .filter(
            Q(post__date_published__isnull=True) | Q(post__date_published__lte=ts),
            Q(post__date_published_end__isnull=True) | Q(post__date_published_end__gt=ts),
        )
        .annotate(sort_date=Coalesce("post__date_published", "post__date_created"))
    )
    # next in list order (new -> old) = older
    next_obj = (
        base.filter(
            Q(sort_date__lt=current_sort_date) |
            Q(sort_date=current_sort_date, post_id__lt=current.post_id)
        )
        .order_by("-sort_date", "-post_id")
        .first()
    )

    # previous in list order = newer
    previous_obj = (
        base.filter(
            Q(sort_date__gt=current_sort_date) |
            Q(sort_date=current_sort_date, post_id__gt=current.post_id)
        )
        .order_by("sort_date", "post_id")
        .last()
    )

    result = {
        "previous": previous_obj.get_absolute_url() if previous_obj else "",
        "next": next_obj.get_absolute_url() if next_obj else "",
    }
    return result