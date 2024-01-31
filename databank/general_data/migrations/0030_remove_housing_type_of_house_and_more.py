# Generated by Django 4.2.6 on 2024-01-11 08:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('general_data', '0029_rename_desease_code_health_disease_disease_code_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='housing',
            name='Type_Of_House',
        ),
        migrations.AlterField(
            model_name='housing',
            name='House_Code',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='general_data.housing_meta'),
        ),
    ]