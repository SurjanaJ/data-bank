# Generated by Django 4.2.6 on 2024-01-22 07:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('general_data', '0032_rename_type_of_public_unitility_public_unitillity_type_of_public_utility'),
    ]

    operations = [
        migrations.RenameField(
            model_name='road',
            old_name='Length_Unit',
            new_name='Length_Unit_Options',
        ),
    ]
