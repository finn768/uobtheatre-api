# Generated by Django 3.2.11 on 2022-01-20 22:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0011_auto_20220108_2216"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="provider_name",
            field=models.CharField(
                choices=[
                    ("CASH", "CASH"),
                    ("CARD", "CARD"),
                    ("SQUARE_POS", "SQUARE_POS"),
                    ("SQUARE_ONLINE", "SQUARE_ONLINE"),
                    ("MANUAL_CARD_REFUND", "MANUAL_CARD_REFUND"),
                    ("SQUARE_REFUND", "SQUARE_REFUND"),
                ],
                max_length=20,
            ),
        ),
    ]
