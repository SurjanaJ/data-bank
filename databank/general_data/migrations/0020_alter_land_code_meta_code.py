# Generated by Django 4.2.6 on 2023-12-07 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('general_data', '0019_tourism_nationality_of_tourism_alter_tourism_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='land_code_meta',
            name='Code',
            field=models.IntegerField(),
        ),
    ]
