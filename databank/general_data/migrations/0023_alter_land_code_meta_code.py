# Generated by Django 4.2.6 on 2023-12-07 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('general_data', '0022_alter_land_code_meta_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='land_code_meta',
            name='Code',
            field=models.IntegerField(default=0),
        ),
    ]
