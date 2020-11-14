# Generated by Django 3.1.3 on 2020-11-13 23:58

from django.db import migrations, models
import django.db.models.deletion
import uobtheatre.utils.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Seat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row', models.CharField(blank=True, max_length=5, null=True)),
                ('number', models.CharField(blank=True, max_length=5, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SeatType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('is_internal', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('internal_capacity', models.SmallIntegerField()),
            ],
            bases=(models.Model, uobtheatre.utils.models.SoftDeletionMixin, uobtheatre.utils.models.TimeStampedMixin),
        ),
        migrations.CreateModel(
            name='SeatGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('capacity', models.IntegerField(null=True)),
                ('seat', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='venues.seat')),
                ('seat_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='venues.seattype')),
                ('venue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seat_groups', to='venues.venue')),
            ],
        ),
    ]
