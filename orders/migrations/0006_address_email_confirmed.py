# Generated by Django 3.0.6 on 2020-05-22 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_auto_20200522_1612'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='email_confirmed',
            field=models.BooleanField(default=False),
        ),
    ]
