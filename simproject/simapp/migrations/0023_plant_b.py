# Generated by Django 5.0.4 on 2024-10-23 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simapp', '0022_plant_planting_cost_plant_revenue'),
    ]

    operations = [
        migrations.AddField(
            model_name='plant',
            name='b',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
