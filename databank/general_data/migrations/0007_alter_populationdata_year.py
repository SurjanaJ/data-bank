# Generated by Django 5.0 on 2024-03-22 04:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('general_data', '0006_alter_hotel_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='populationdata',
            name='Year',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
