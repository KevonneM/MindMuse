# Generated by Django 4.2.1 on 2023-06-15 18:01

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("second_brain", "0015_quoteoftheday"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="quoteoftheday",
            name="updated_at",
        ),
    ]