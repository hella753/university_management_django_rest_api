# Generated by Django 5.1.4 on 2024-12-11 14:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0010_rename_time_lecture_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='lecture',
            name='end_time',
            field=models.TimeField(default=datetime.time(0, 0), verbose_name='End Time'),
        ),
    ]
