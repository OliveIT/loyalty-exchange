# Generated by Django 2.0.1 on 2019-01-21 15:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0006_auto_20190121_1528'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='membership',
            name='points',
        ),
    ]
