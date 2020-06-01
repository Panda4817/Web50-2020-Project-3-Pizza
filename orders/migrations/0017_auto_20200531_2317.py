# Generated by Django 3.0.6 on 2020-05-31 22:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0016_auto_20200529_1719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='food',
            name='size',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.Size'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('checkout', 'checkout'), ('confirmed', 'confirmed'), ('preparing', 'preparing'), ('ready to collect', 'ready to collect'), ('collected', 'collected'), ('out for delivery', 'out for delivery'), ('delivered', 'delivered'), ('completed', 'completed')], default='checkout', max_length=64),
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
