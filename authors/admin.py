from django import forms
from django.contrib import admin
from parler.admin import TranslatableAdmin

from .models import AuthorProfile, SocialLink


# --- AuthorProfile Admin ---

class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 1


@admin.register(AuthorProfile)
class AuthorProfileAdmin(TranslatableAdmin):
    list_display = ("name",)
    search_fields = ("name", "translations__role")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("name", "slug", "role")}),
        ("Details", {"fields": ("bio", "photo")}),
    )
    inlines = [SocialLinkInline]


# --- Override djangocms-stories PostAdmin to use AuthorProfile ---

class AuthorProfileChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


def _override_post_admin():
    from djangocms_stories.admin import PostAdmin
    from djangocms_stories.models import Post

    class CustomPostForm(forms.ModelForm):
        author_profile = AuthorProfileChoiceField(
            queryset=AuthorProfile.objects.all(),
            required=False,
            label="Author",
        )

        class Meta:
            model = Post
            fields = "__all__"

    class CustomPostAdmin(PostAdmin):
        form = CustomPostForm

        def get_form(self, request, obj=None, **kwargs):
            form = super().get_form(request, obj, **kwargs)
            if obj and obj.author_id:
                try:
                    profile = AuthorProfile.objects.get(user=obj.author)
                    form.base_fields["author_profile"].initial = profile.pk
                except AuthorProfile.DoesNotExist:
                    pass
            return form

        def get_fieldsets(self, request, obj=None):
            fieldsets = super().get_fieldsets(request, obj)
            new_fieldsets = []
            for name, opts in fieldsets:
                fields = opts.get("fields", [])
                new_fields = []
                for field in fields:
                    if field == "author":
                        new_fields.append("author_profile")
                    elif isinstance(field, (list, tuple)):
                        new_fields.append(
                            type(field)(
                                f if f != "author" else "author_profile"
                                for f in field
                            )
                        )
                    else:
                        new_fields.append(field)
                new_fieldsets.append((name, {**opts, "fields": new_fields}))
            return new_fieldsets

        def save_model(self, request, obj, form, change):
            profile = form.cleaned_data.get("author_profile")
            if profile:
                obj.author = profile.user
            super().save_model(request, obj, form, change)

    if admin.site.is_registered(Post):
        admin.site.unregister(Post)
    admin.site.register(Post, CustomPostAdmin)


try:
    _override_post_admin()
except Exception:
    pass
