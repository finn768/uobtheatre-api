# Generated by Django 3.2.10 on 2022-01-13 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("venues", "0003_alter_venue_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="venue",
            name="internal_capacity",
            field=models.PositiveSmallIntegerField(),
        ),
    ]