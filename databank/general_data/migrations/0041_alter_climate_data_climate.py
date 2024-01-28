# Generated by Django 5.0 on 2024-01-28 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('general_data', '0040_climate_place_meta_climate_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='climate_data',
            name='Climate',
            field=models.CharField(choices=[('Rain', 'Rain'), ('Snow', 'Snow'), ('Storm', 'Storm')], default=1, max_length=20),
            preserve_default=False,
        ),
    ]