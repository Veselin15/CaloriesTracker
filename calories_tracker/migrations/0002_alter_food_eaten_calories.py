# Generated by Django 5.2.1 on 2025-07-12 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calories_tracker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='food_eaten',
            name='calories',
            field=models.FloatField(),
        ),
    ]
