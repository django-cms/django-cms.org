from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("name", "membership_type", "sort_order")
    list_filter = ("membership_type",)
    list_editable = ("sort_order",)
    search_fields = ("name",)
    fieldsets = (
        (None, {"fields": ("name", "logo", "membership_type")}),
        (_("Details"), {"fields": ("link", "description", "sort_order")}),
    )
