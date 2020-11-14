# Generated by Django 3.1.3 on 2020-11-14 15:35

from django.db import migrations, models
import uobtheatre.utils.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Society",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
            bases=(
                models.Model,
                uobtheatre.utils.models.SoftDeletionMixin,
                uobtheatre.utils.models.TimeStampedMixin,
            ),
        ),
    ]