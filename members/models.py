from django.db import models
from django.utils.translation import gettext_lazy as _
from filer.fields.image import FilerImageField


class MembershipType(models.TextChoices):
    PLATINUM = "platinum", _("Platinum")
    GOLD = "gold", _("Gold")
    SILVER = "silver", _("Silver")
    BRONZE = "bronze", _("Bronze")
    COMMUNITY = "community", _("Community")


class Member(models.Model):
    name = models.CharField(_("name"), max_length=200)
    logo = FilerImageField(
        verbose_name=_("logo"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    membership_type = models.CharField(
        _("membership type"),
        max_length=20,
        choices=MembershipType.choices,
        default=MembershipType.COMMUNITY,
    )
    link = models.URLField(_("link"), blank=True)
    description = models.TextField(_("description"), blank=True)
    sort_order = models.PositiveSmallIntegerField(_("order"), default=0)

    class Meta:
        verbose_name = _("Member")
        verbose_name_plural = _("Members")
        ordering = ("sort_order", "name")

    def __str__(self):
        return self.name
