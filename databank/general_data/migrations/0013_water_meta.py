# Generated by Django 4.2.6 on 2023-12-03 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('general_data', '0012_hotel'),
    ]

    operations = [
        migrations.CreateModel(
            name='Water_Meta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Code', models.CharField(max_length=100)),
                ('Water_Type', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
