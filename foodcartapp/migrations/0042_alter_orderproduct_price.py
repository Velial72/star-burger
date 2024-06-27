# Generated by Django 5.0.6 on 2024-06-26 18:24

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0041_alter_orderproduct_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderproduct',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Стоимость'),
        ),
    ]
