# Generated by Django 4.2.6 on 2023-12-05 08:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('general_data', '0015_land_country'),
    ]

    operations = [
        migrations.RenameField(
            model_name='land',
            old_name='year',
            new_name='Year',
        ),
    ]
