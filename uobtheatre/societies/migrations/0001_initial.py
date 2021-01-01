# Generated by Django 3.1.4 on 2021-01-01 16:44

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
                ("logo", models.ImageField(upload_to="")),
            ],
            bases=(models.Model, uobtheatre.utils.models.TimeStampedMixin),
        ),
    ]
