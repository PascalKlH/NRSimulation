# Generated by Django 5.0.4 on 2024-10-14 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simapp', '0015_alter_weather_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weather',
            name='date',
            field=models.CharField(default="2021-01-01 00:00:00", max_length=100),
        ),
    ]