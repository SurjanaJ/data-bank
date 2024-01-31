# Generated by Django 4.2.6 on 2024-01-25 10:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trade_data', '0011_alter_tradedata_tarrif'),
        ('general_data', '0041_delete_road'),
    ]

    operations = [
        migrations.CreateModel(
            name='Road',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Year', models.IntegerField()),
                ('Highway_No', models.CharField(blank=True, max_length=50, null=True)),
                ('Name_Of_The_Road', models.CharField(blank=True, max_length=50, null=True)),
                ('Length_Unit_Options', models.CharField(blank=True, choices=[('KM', 'KM')], max_length=20, null=True)),
                ('Length', models.IntegerField(blank=True, default=0, null=True)),
                ('Code_Type_Of_Road', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general_data.road_meta')),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade_data.country_meta')),
            ],
        ),
    ]