import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("filer", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Member",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200, verbose_name="name")),
                (
                    "membership_type",
                    models.CharField(
                        choices=[
                            ("platinum", "Platinum"),
                            ("gold", "Gold"),
                            ("silver", "Silver"),
                            ("bronze", "Bronze"),
                            ("community", "Community"),
                        ],
                        default="community",
                        max_length=20,
                        verbose_name="membership type",
                    ),
                ),
                ("link", models.URLField(blank=True, verbose_name="link")),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="description"),
                ),
                (
                    "sort_order",
                    models.PositiveSmallIntegerField(default=0, verbose_name="order"),
                ),
                (
                    "logo",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="filer.image",
                        verbose_name="logo",
                    ),
                ),
            ],
            options={
                "verbose_name": "Member",
                "verbose_name_plural": "Members",
                "ordering": ("sort_order", "name"),
            },
        ),
    ]
