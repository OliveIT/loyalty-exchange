# Generated by Django 2.0.1 on 2019-01-22 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0007_remove_membership_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='eth_public_key',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='myuser',
            name='eth_secret_key',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
