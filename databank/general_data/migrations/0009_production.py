# Generated by Django 5.0 on 2024-03-01 09:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('general_data', '0008_production_meta'),
    ]

    operations = [
        migrations.CreateModel(
            name='Production',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Producer_Name', models.CharField(max_length=200)),
                ('Province', models.CharField(max_length=100)),
                ('District', models.CharField(max_length=100)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('Code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general_data.production_meta')),
            ],
        ),
    ]
