# Generated by Django 3.0.6 on 2020-05-25 11:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_address_email_confirmed'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='extra_for_sub',
            new_name='ExtraForSub',
        ),
        migrations.RenameModel(
            old_name='type',
            new_name='FoodType',
        ),
        migrations.RenameModel(
            old_name='order_to_food',
            new_name='OrderToFood',
        ),
        migrations.RenameField(
            model_name='food',
            old_name='type',
            new_name='food_type',
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_type',
            field=models.CharField(default='delivery', max_length=64),
        ),
        migrations.AlterField(
            model_name='food',
            name='size',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.Size'),
        ),
        migrations.AlterField(
            model_name='ordertofood',
            name='food_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.Food'),
        ),
        migrations.AlterField(
            model_name='ordertofood',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.Order'),
        ),
        migrations.AlterField(
            model_name='ordertofood',
            name='topping',
            field=models.ManyToManyField(blank=True, to='orders.Topping'),
        ),
    ]
