# Generated by Django 4.2.4 on 2023-09-14 21:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0005_payment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="transaction_id",
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
    ]
