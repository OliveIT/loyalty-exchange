# Generated by Django 2.0.1 on 2019-01-23 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0009_auto_20190123_0259'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='birth',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='phone',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='wallet',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='extra_points',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=16),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='company_name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]