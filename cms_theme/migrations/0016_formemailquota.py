from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cms_theme", "0015_milestonecard"),
    ]

    operations = [
        migrations.CreateModel(
            name="FormEmailQuota",
            fields=[
                (
                    "key",
                    models.CharField(max_length=64, primary_key=True, serialize=False),
                ),
                ("count", models.PositiveIntegerField(default=0)),
                ("expires_at", models.DateTimeField(db_index=True)),
            ],
            options={
                "verbose_name": "form email quota",
                "verbose_name_plural": "form email quotas",
            },
        ),
    ]
