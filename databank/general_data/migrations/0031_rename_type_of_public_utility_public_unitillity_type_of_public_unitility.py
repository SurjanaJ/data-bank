# Generated by Django 4.2.6 on 2024-01-11 09:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('general_data', '0030_remove_housing_type_of_house_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='public_unitillity',
            old_name='Type_Of_Public_Utility',
            new_name='Type_Of_Public_Unitility',
        ),
    ]