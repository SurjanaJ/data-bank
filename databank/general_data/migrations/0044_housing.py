# Generated by Django 4.2.6 on 2024-01-25 11:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trade_data', '0011_alter_tradedata_tarrif'),
        ('general_data', '0043_delete_housing'),
    ]

    operations = [
        migrations.CreateModel(
            name='Housing',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Year', models.IntegerField()),
                ('City', models.CharField(blank=True, null=True)),
                ('Number', models.IntegerField(blank=True, default=0, null=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('created_date', models.DateTimeField(auto_now=True)),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade_data.country_meta')),
                ('House_Code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general_data.housing_meta')),
            ],
        ),
    ]
