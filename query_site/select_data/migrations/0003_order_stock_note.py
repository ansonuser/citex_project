# Generated by Django 3.0.4 on 2020-04-15 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('select_data', '0002_auto_20200415_2027'),
    ]

    operations = [
        migrations.AddField(
            model_name='order_stock',
            name='note',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
