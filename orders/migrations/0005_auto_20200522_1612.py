# Generated by Django 3.0.6 on 2020-05-22 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='street_address_2',
            field=models.CharField(blank=True, max_length=64),
        ),
    ]
