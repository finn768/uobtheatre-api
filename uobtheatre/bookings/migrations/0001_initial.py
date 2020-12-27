# Generated by Django 3.1.4 on 2020-12-27 11:50

from django.db import migrations, models
import django.db.models.deletion
import uobtheatre.utils.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('productions', '0001_initial'),
        ('venues', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_reference', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('performance', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='bookings', to='productions.performance')),
            ],
            bases=(models.Model, uobtheatre.utils.models.TimeStampedMixin),
        ),
        migrations.CreateModel(
            name='ConcessionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('discount', models.FloatField()),
                ('performances', models.ManyToManyField(blank=True, related_name='discounts', to='productions.Performance')),
                ('seat_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='venues.seatgroup')),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tickets', to='bookings.booking')),
                ('concession_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='seat_bookings', to='bookings.concessiontype')),
                ('seat', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='venues.seat')),
                ('seat_group', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='tickets', to='venues.seatgroup')),
            ],
        ),
        migrations.CreateModel(
            name='DiscountRequirement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.SmallIntegerField()),
                ('concession_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookings.concessiontype')),
                ('discount', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discount_requirements', to='bookings.discount')),
            ],
        ),
    ]
