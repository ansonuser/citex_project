# Generated by Django 3.0.4 on 2020-04-15 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('select_data', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order_stock',
            name='order_stock_status',
            field=models.IntegerField(default=0),
        ),
    ]
