# Generated by Django 2.0.1 on 2019-01-24 01:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0013_membership_rate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='rate',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=16),
        ),
        migrations.AlterUniqueTogether(
            name='membership',
            unique_together={('profile', 'service')},
        ),
    ]