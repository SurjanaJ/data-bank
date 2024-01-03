# Generated by Django 4.2.6 on 2024-01-03 10:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trade_data', '0007_hs_code_meta_created_date_hs_code_meta_modified_date_and_more'),
        ('general_data', '0027_disaster_data_meta_energy_meta_health_disease_meta_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Road',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Year', models.DateField(blank=True, null=True)),
                ('Highway_No', models.CharField(blank=True, max_length=50, null=True)),
                ('Name_Of_The_Road', models.CharField(blank=True, max_length=50, null=True)),
                ('Length_Unit', models.CharField(blank=True, choices=[('KM', 'KM')], max_length=20, null=True)),
                ('Length', models.IntegerField(blank=True, default=0, null=True)),
                ('Code_Type_Of_Road', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general_data.road_meta')),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade_data.country_meta')),
            ],
        ),
    ]
