# Generated by Django 5.0.7 on 2024-08-06 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="otp",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]
