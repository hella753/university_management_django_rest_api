# Generated by Django 5.1.4 on 2024-12-18 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0031_semester'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lecture',
            name='semester',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Semester'),
        ),
        migrations.AlterField(
            model_name='registrationaccess',
            name='semester',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Semester'),
        ),
    ]
