# Generated by Django 5.1.4 on 2024-12-18 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0029_alter_lecture_capacity_alter_lecture_day_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='max_points',
            field=models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Max points'),
        ),
    ]
