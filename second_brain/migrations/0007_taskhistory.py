# Generated by Django 4.2 on 2023-05-10 20:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("second_brain", "0006_alter_task_completion_goal"),
    ]

    operations = [
        migrations.CreateModel(
            name="TaskHistory",
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
                ("title", models.CharField(max_length=100)),
                ("description", models.TextField()),
                (
                    "priority",
                    models.CharField(
                        blank=True,
                        choices=[("L", "Low"), ("M", "Medium"), ("H", "High")],
                        max_length=1,
                        null=True,
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("P", "Physical"),
                            ("M", "Mental"),
                            ("S", "Spiritual"),
                        ],
                        max_length=1,
                    ),
                ),
                (
                    "frequency",
                    models.CharField(
                        choices=[("D", "Daily"), ("W", "Weekly"), ("M", "Monthly")],
                        max_length=1,
                    ),
                ),
                ("completion_goal", models.PositiveIntegerField(blank=True, null=True)),
                ("completion_count", models.PositiveIntegerField(default=0)),
                ("status", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="second_brain.task",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
