# Generated by Django 5.0 on 2024-03-25 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade_data', '0011_alter_tradedata_tarrif'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradedata',
            name='Calender',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]