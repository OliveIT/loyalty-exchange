# Generated by Django 2.0.1 on 2019-01-25 03:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0018_auto_20190125_0153'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransferTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=6, default=0, max_digits=16)),
                ('confirmed', models.BooleanField(default=False, help_text='User should click the link sent to their email', verbose_name='confirmed')),
                ('otp_code', models.CharField(max_length=100)),
                ('status', models.CharField(default='Unconfirmed', max_length=100)),
                ('burn_tx_hash', models.CharField(blank=True, default='', max_length=100)),
                ('mint_tx_hash', models.CharField(blank=True, default='', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiving_user', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sending_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='redeemtransaction',
            name='tx_hash',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
