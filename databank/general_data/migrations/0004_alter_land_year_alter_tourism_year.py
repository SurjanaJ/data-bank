# Generated by Django 5.0 on 2024-03-22 02:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('general_data', '0003_alter_transport_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='land',
            name='Year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='tourism',
            name='Year',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
