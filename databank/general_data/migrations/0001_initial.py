# Generated by Django 4.2.6 on 2024-02-06 10:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('trade_data', '0011_alter_tradedata_tarrif'),
    ]

    operations = [
        migrations.CreateModel(
            name='Crime_Meta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Code', models.CharField(max_length=100)),
                ('Name', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Disaster_Data_Meta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Code', models.CharField(max_length=100)),
                ('Disaster_Type', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Education_Degree_Meta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Code', models.CharField(max_length=20)),
                ('Degree', models.TextField(blank=True, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Education_Level_Meta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Code', models.CharField(max_length=20)),
                ('Level', models.TextField(blank=True, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Energy_Meta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Code', models.CharField(max_length=100)),
                ('Energy_Type', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Health_disease_Meta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Code', models.CharField(max_length=100)),
                ('Disease_Type', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Housing_Meta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Code', models.CharField(max_length=100)),
                ('House_Type', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Land_Code_Meta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Code', models.CharField()),
                ('Land_Type', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Mine_Meta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Code', models.CharField(max_length=100)),
                ('Mine_Type', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Occupation_Meta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('SOC_Code', models.CharField(max_length=100)),
                ('SOC_Group', models.TextField(blank=True, null=True)),
                ('SOC_Title', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Road_Meta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Code', models.CharField(max_length=100)),
                ('Road_Type', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Services_Meta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Code', models.CharField(max_length=100)),
                ('Services_Type', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tourism_Meta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Code', models.CharField(max_length=100)),
                ('Arrival_Mode', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Transport_Meta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Code', models.CharField(max_length=100)),
                ('Transport_Type', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Water_Meta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Code', models.CharField(max_length=100)),
                ('Water_Type', models.TextField(blank=True, null=True)),
            ],
        ),
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
        migrations.CreateModel(
            name='Transport',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Year', models.DateField(blank=True, null=True)),
                ('Unit', models.CharField(blank=True, choices=[('Metric Ton', 'Metric Ton')], max_length=10, null=True)),
                ('Quantity', models.DecimalField(blank=True, decimal_places=3, max_digits=100, null=True)),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade_data.country_meta')),
                ('Transport_Classification_Code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general_data.transport_meta')),
            ],
        ),
        migrations.CreateModel(
            name='Tourism',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Year', models.DateField(blank=True, null=True)),
                ('Number_Of_Tourist', models.IntegerField(blank=True, null=True)),
                ('Number', models.IntegerField(blank=True, default=0, null=True)),
                ('Arrival_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general_data.tourism_meta')),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Tourism_Country', to='trade_data.country_meta')),
                ('Nationality_Of_Tourism', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Tourism_Nationality_Of_Tourism', to='trade_data.country_meta')),
            ],
        ),
        migrations.CreateModel(
            name='Services',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Year', models.DateField(blank=True, null=True)),
                ('Direction', models.CharField(blank=True, choices=[('Import', 'Import'), ('Export', 'Export')], max_length=10, null=True)),
                ('Value', models.FloatField(blank=True, max_length=100, null=True)),
                ('Code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general_data.services_meta')),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services_country', to='trade_data.country_meta')),
                ('Origin_Destination', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services_origin_destination', to='trade_data.country_meta')),
            ],
        ),
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
        migrations.CreateModel(
            name='Public_Unitillity',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Year', models.DateField(blank=True, null=True)),
                ('Type_Of_Public_Utility', models.CharField(blank=True, max_length=100, null=True)),
                ('Number', models.IntegerField(blank=True, default=0, null=True)),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade_data.country_meta')),
            ],
        ),
        migrations.CreateModel(
            name='PopulationData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Year', models.DateField(blank=True, null=True)),
                ('Gender', models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female')], max_length=10, null=True)),
                ('Age_Group', models.CharField(blank=True, choices=[('0-14', '0-14'), ('15-64', '15-64'), ('64+', '64+')], max_length=10, null=True)),
                ('Population', models.IntegerField(blank=True, default=0, null=True)),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade_data.country_meta')),
            ],
        ),
        migrations.CreateModel(
            name='Political_Data',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Year', models.DateField(blank=True, null=True)),
                ('Political_Party_Name', models.CharField(blank=True, max_length=30, null=True)),
                ('Number_Of_Member', models.IntegerField(blank=True, default=0, null=True)),
                ('Province', models.CharField(blank=True, max_length=30, null=True)),
                ('District', models.CharField(blank=True, max_length=30, null=True)),
                ('Municipality', models.CharField(blank=True, max_length=30, null=True)),
                ('Wards', models.CharField(blank=True, max_length=30, null=True)),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade_data.country_meta')),
            ],
        ),
        migrations.CreateModel(
            name='Occupation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Year', models.IntegerField()),
                ('Number', models.IntegerField()),
                ('Code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general_data.occupation_meta')),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade_data.country_meta')),
            ],
        ),
        migrations.CreateModel(
            name='Mining',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Year', models.DateField(blank=True, null=True)),
                ('Unit', models.CharField(blank=True, choices=[('Mt', 'Mt')], max_length=10, null=True)),
                ('Current_Production', models.IntegerField(blank=True, default=0, null=True)),
                ('Potential_Stock', models.IntegerField(blank=True, default=0, null=True)),
                ('Mining_Company_Name', models.CharField(blank=True, max_length=100, null=True)),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade_data.country_meta')),
                ('Name_Of_Mine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general_data.mine_meta')),
            ],
        ),
        migrations.CreateModel(
            name='Land',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Year', models.DateField(blank=True, null=True)),
                ('Unit', models.CharField(blank=True, choices=[('Ha', 'Ha')], max_length=10, null=True)),
                ('Area', models.DecimalField(blank=True, decimal_places=3, max_digits=100, null=True)),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade_data.country_meta')),
                ('Land_Code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general_data.land_code_meta')),
            ],
        ),
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
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Year', models.DateField(blank=True, null=True)),
                ('Name_Of_The_Hotel', models.CharField(blank=True, null=True)),
                ('Capacity_Room', models.IntegerField(blank=True, default=0, null=True)),
                ('Occupancy_In_Year', models.IntegerField(blank=True, default=0, null=True)),
                ('City', models.CharField(blank=True, null=True)),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade_data.country_meta')),
            ],
        ),
        migrations.CreateModel(
            name='Health_disease',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Year', models.IntegerField()),
                ('Unit', models.CharField(blank=True, choices=[('Person', 'Person')], max_length=20, null=True)),
                ('Number_Of_Case', models.IntegerField(blank=True, default=0, null=True)),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade_data.country_meta')),
                ('Disease_Code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general_data.health_disease_meta')),
            ],
        ),
        migrations.CreateModel(
            name='ForestData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Year', models.DateField(blank=True, null=True)),
                ('Name_Of_The_Plant', models.CharField(max_length=100)),
                ('Scientific_Name', models.CharField(max_length=100)),
                ('Local_Name', models.CharField(max_length=100)),
                ('Stock_Unit', models.CharField(blank=True, choices=[('Cu Mtr', 'Cu Mtr')], max_length=50, null=True)),
                ('Stock_Available', models.IntegerField(blank=True, default=0, null=True)),
                ('Area_Unit', models.CharField(blank=True, choices=[('Hector', 'Hector')], max_length=100, null=True)),
                ('Area_Covered', models.DecimalField(blank=True, decimal_places=3, max_digits=100, null=True)),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade_data.country_meta')),
            ],
        ),
        migrations.CreateModel(
            name='Energy',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Year', models.DateField(blank=True, null=True)),
                ('Potential_Unit', models.CharField(blank=True, choices=[('Mt', 'Mt')], max_length=10, null=True)),
                ('Potential_Capacity_MW', models.IntegerField(blank=True, default=0, null=True)),
                ('Unit_Production', models.CharField(blank=True, choices=[('Megawat', 'Megawat')], max_length=20, null=True)),
                ('Current_Production_In_MW', models.IntegerField(blank=True, default=0, null=True)),
                ('Name_Of_The_Generating_Company', models.CharField(blank=True, max_length=100, null=True)),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade_data.country_meta')),
                ('Power_Category_Code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general_data.energy_meta')),
            ],
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Male', models.BigIntegerField(default=0)),
                ('Female', models.BigIntegerField(default=0)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('Degree_Code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general_data.education_degree_meta')),
                ('Level_Code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general_data.education_level_meta')),
            ],
        ),
        migrations.CreateModel(
            name='Disaster_Data',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Year', models.IntegerField()),
                ('Human_Loss', models.IntegerField(blank=True, default=0, null=True)),
                ('Animal_Loss', models.IntegerField(blank=True, default=0, null=True)),
                ('Physical_Properties_Loss_In_USD', models.IntegerField(blank=True, default=0, null=True)),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade_data.country_meta')),
                ('Disaster_Code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general_data.disaster_data_meta')),
            ],
        ),
        migrations.CreateModel(
            name='Crime',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Year', models.DateField(blank=True, null=True)),
                ('Gender', models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female')], max_length=10, null=True)),
                ('Age', models.IntegerField(blank=True, null=True)),
                ('District', models.CharField(blank=True, max_length=50, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('Code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general_data.crime_meta')),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade_data.country_meta')),
            ],
        ),
        migrations.CreateModel(
            name='Climate_Place_Meta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Place_Code', models.CharField(max_length=20)),
                ('Place_Name', models.TextField()),
                ('created_date', models.DateTimeField(auto_now=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade_data.country_meta')),
            ],
        ),
        migrations.CreateModel(
            name='Climate_Data',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Date', models.DateField()),
                ('Max_Temperature', models.FloatField(max_length=100)),
                ('Min_Temperature', models.FloatField(max_length=100)),
                ('Climate', models.CharField(choices=[('Rain', 'Rain'), ('Snow', 'Snow'), ('Storm', 'Storm')], max_length=20)),
                ('Amount', models.FloatField(max_length=100)),
                ('Climate_Unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='generaldata_climate_unit', to='trade_data.unit_meta')),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade_data.country_meta')),
                ('Place', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general_data.climate_place_meta')),
                ('Temperature_Unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='generaldata_temperature_unit', to='trade_data.unit_meta')),
            ],
        ),
        migrations.CreateModel(
            name='Budgetary_Data',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Fiscal_Year', models.CharField(blank=True, max_length=10, null=True)),
                ('Amount_In_USD', models.IntegerField(blank=True, default=0, null=True)),
                ('Prefered_Denomination', models.CharField(blank=True, max_length=30, null=True)),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade_data.country_meta')),
            ],
        ),
    ]
