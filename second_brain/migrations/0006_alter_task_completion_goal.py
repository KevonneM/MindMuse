# Generated by Django 4.2 on 2023-05-08 20:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("second_brain", "0005_alter_task_completion_count_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="completion_goal",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
