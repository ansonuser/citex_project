# Generated by Django 3.0.4 on 2020-03-29 12:13

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('select_data', '0002_auto_20200328_2035'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='product',
            managers=[
                ('record', django.db.models.manager.Manager()),
            ],
        ),
    ]
