from django import template
from djangocms_stories.models import PostCategory

register = template.Library()


@register.simple_tag
def get_blog_categories():
    return PostCategory.objects.order_by("priority", "translations__name")
