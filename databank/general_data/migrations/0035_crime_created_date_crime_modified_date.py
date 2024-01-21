# Generated by Django 5.0 on 2024-01-19 11:11

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('general_data', '0034_alter_crime_district'),
    ]

    operations = [
        migrations.AddField(
            model_name='crime',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='crime',
            name='modified_date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]