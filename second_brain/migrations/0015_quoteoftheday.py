# Generated by Django 4.2.1 on 2023-06-15 18:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("second_brain", "0014_quote_starred"),
    ]

    operations = [
        migrations.CreateModel(
            name="QuoteOfTheDay",
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
                ("quote", models.CharField(max_length=255)),
                ("author", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
