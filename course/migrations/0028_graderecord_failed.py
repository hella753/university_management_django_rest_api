# Generated by Django 5.1.4 on 2024-12-17 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0027_registrationaccess_semester_end_date_graderecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='graderecord',
            name='failed',
            field=models.BooleanField(default=False, verbose_name='Failed'),
        ),
    ]