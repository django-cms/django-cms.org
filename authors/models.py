from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from filer.fields.image import FilerImageField
from parler.models import TranslatableModel, TranslatedFields


class AuthorProfile(TranslatableModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="author_profile",
        editable=False,
    )
    name = models.CharField(_("name"), max_length=200)
    slug = models.SlugField(_("slug"), unique=True)
    photo = FilerImageField(
        verbose_name=_("photo"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    translations = TranslatedFields(
        role=models.CharField(_("role"), max_length=200, blank=True),
        bio=models.TextField(_("bio"), blank=True),
    )

    class Meta:
        verbose_name = _("Author Profile")
        verbose_name_plural = _("Author Profiles")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        if not self.user_id:
            username = f"author-{self.slug}"
            user = User.objects.create(
                username=username,
                first_name=self.name,
                is_active=False,
            )
            self.user = user
        else:
            self.user.first_name = self.name
            self.user.save(update_fields=["first_name"])
        super().save(*args, **kwargs)


class SocialLink(models.Model):
    author = models.ForeignKey(
        AuthorProfile,
        on_delete=models.CASCADE,
        related_name="social_links",
    )
    icon = models.CharField(
        _("icon class"),
        max_length=100,
        blank=True,
        help_text=_('CSS class, e.g. "bi bi-github" or "fa-brands fa-discord"'),
    )
    label = models.CharField(_("label"), max_length=100)
    url = models.CharField(
        _("link"),
        max_length=500,
        help_text=_('URL, mailto:email@example.com, or tel:+49123456789'),
    )
    sort_order = models.PositiveSmallIntegerField(_("order"), default=0)

    class Meta:
        verbose_name = _("Social Link")
        verbose_name_plural = _("Social Links")
        ordering = ("sort_order",)

    def __str__(self):
        return self.label
