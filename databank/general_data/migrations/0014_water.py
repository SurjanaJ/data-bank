# Generated by Django 4.2.6 on 2023-12-03 11:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trade_data', '0003_alter_tradedata_tarrif'),
        ('general_data', '0013_water_meta'),
    ]

    operations = [
        migrations.CreateModel(
            name='Water',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Year', models.DateField(blank=True, null=True)),
                ('Description', models.CharField(blank=True, null=True)),
                ('Unit', models.CharField(blank=True, choices=[('Cu Metre', 'Cu Metre')], max_length=10, null=True)),
                ('Volume', models.DecimalField(blank=True, decimal_places=3, max_digits=100, null=True)),
                ('Name_Of_The_River', models.CharField(blank=True, max_length=100, null=True)),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade_data.country_meta')),
                ('Water_Type_Code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general_data.water_meta')),
            ],
        ),
    ]