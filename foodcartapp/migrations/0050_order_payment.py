# Generated by Django 5.0.6 on 2024-06-27 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0049_order_called_at_order_delivered_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.CharField(choices=[('C', 'Наличностью'), ('O', 'Онлайн'), ('CC', 'Картой')], db_index=True, default='C', max_length=10, verbose_name='Способ оплаты'),
        ),
    ]
