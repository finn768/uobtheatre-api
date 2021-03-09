# Generated by Django 3.1.7 on 2021-03-09 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Address",
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
                ("building_name", models.CharField(max_length=255, null=True)),
                ("building_number", models.CharField(max_length=10, null=True)),
                ("street", models.CharField(max_length=255)),
                ("city", models.CharField(max_length=255)),
                ("postcode", models.CharField(max_length=9)),
                ("latitude", models.FloatField(blank=True, null=True)),
                ("longitude", models.FloatField(blank=True, null=True)),
            ],
        ),
    ]
