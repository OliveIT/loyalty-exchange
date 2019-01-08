# Generated by Django 2.0.1 on 2019-01-08 10:01

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrencyRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(default='USD', max_length=100)),
                ('rate', models.CharField(default='1', max_length=100)),
                ('updated_ts', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField(default=0)),
                ('install_ts', models.DateTimeField(auto_now_add=True)),
                ('update_ts', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RenameField(
            model_name='service',
            old_name='code',
            new_name='description',
        ),
        migrations.RemoveField(
            model_name='service',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='service',
            name='style',
        ),
        migrations.AddField(
            model_name='service',
            name='country',
            field=models.CharField(choices=[('CA', 'CA'), ('DE', 'DE'), ('FR', 'FR'), ('UK', 'UK'), ('US', 'US')], default='US', max_length=100),
        ),
        migrations.AddField(
            model_name='service',
            name='subscribers',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='service',
            name='is_opened',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='service',
            name='service_type',
            field=models.CharField(choices=[('airline', 'airline'), ('gym', 'gym'), ('mart', 'mart'), ('spa', 'spa'), ('taxi', 'taxi')], default='airline', max_length=100),
        ),
        migrations.AlterField(
            model_name='service',
            name='title',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
