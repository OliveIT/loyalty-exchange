# Generated by Django 2.0.1 on 2019-01-25 13:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0020_auto_20190125_0828'),
    ]

    operations = [
        migrations.AlterField(
            model_name='redeemtransaction',
            name='service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='services.Service'),
        ),
    ]
