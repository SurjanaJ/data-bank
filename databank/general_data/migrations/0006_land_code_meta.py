# Generated by Django 4.2.6 on 2023-12-03 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('general_data', '0005_populationdata'),
    ]

    operations = [
        migrations.CreateModel(
            name='Land_Code_Meta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Code', models.CharField(max_length=100)),
                ('Land_Type', models.TextField(blank=True, null=True)),
            ],
        ),
    ]