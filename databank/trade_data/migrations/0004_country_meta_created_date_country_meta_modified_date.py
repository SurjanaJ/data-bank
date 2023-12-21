# Generated by Django 4.2.6 on 2023-12-19 06:20

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('trade_data', '0003_alter_tradedata_tarrif'),
    ]

    operations = [
        migrations.AddField(
            model_name='country_meta',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='country_meta',
            name='modified_date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
