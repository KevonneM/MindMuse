# Generated by Django 4.2 on 2023-04-18 22:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_alter_customuser_age"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="last_tracked_city",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
