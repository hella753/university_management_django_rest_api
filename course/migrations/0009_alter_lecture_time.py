# Generated by Django 5.1.4 on 2024-12-11 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0008_assignment_max_points_alter_grade_grade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lecture',
            name='time',
            field=models.TimeField(verbose_name='Start Time'),
        ),
    ]