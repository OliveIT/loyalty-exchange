# Generated by Django 2.0.1 on 2019-01-25 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0017_auto_20190124_1235'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='service',
            options={'ordering': ('created_at',)},
        ),
        migrations.RenameField(
            model_name='service',
            old_name='created',
            new_name='created_at',
        ),
        migrations.AlterField(
            model_name='service',
            name='title',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
    ]