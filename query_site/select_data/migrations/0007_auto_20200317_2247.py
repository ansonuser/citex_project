# Generated by Django 3.0.4 on 2020-03-17 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('select_data', '0006_auto_20200317_2224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order_detail',
            name='actual_ship_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='order_detail',
            name='expected_ship_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='order_detail',
            name='last_modified',
            field=models.DateField(auto_now=True),
        ),
    ]
