from django import template
from djangocms_stories.models import PostCategory

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
