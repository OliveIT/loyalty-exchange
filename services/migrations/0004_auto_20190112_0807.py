# Generated by Django 2.0.1 on 2019-01-12 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_auto_20190112_0701'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='phone',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]