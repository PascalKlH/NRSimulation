# Generated by Django 5.0.4 on 2024-10-29 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simapp', '0024_datamodeloutput_profit_datamodeloutput_rain_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='datamodeloutput',
            name='num_plants',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
