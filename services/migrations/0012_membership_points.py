# Generated by Django 2.0.1 on 2019-01-23 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0011_auto_20190123_1356'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='points',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=16),
        ),
    ]