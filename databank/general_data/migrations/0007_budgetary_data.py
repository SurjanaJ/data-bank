# Generated by Django 5.0 on 2024-02-29 10:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('general_data', '0006_delete_budgetary_data'),
        ('trade_data', '0011_alter_tradedata_tarrif'),
    ]

    operations = [
        migrations.CreateModel(
            name='Budgetary_Data',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Fiscal_Year', models.CharField(max_length=30)),
                ('Amount_In_USD', models.FloatField(default=0.0)),
                ('Prefered_Denomination', models.CharField(max_length=100)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade_data.country_meta')),
            ],
        ),
    ]