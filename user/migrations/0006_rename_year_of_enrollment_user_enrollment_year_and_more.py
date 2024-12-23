# Generated by Django 5.1.4 on 2024-12-11 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_attendance'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='year_of_enrollment',
            new_name='enrollment_year',
        ),
        migrations.RemoveField(
            model_name='attendance',
            name='is_present',
        ),
        migrations.AddField(
            model_name='attendance',
            name='first_hour',
            field=models.BooleanField(default=False, verbose_name='First hour'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='second_hour',
            field=models.BooleanField(default=False, verbose_name='Second hour'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='third_hour',
            field=models.BooleanField(default=False, verbose_name='Third hour'),
        ),
        migrations.AddField(
            model_name='user',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True, verbose_name='Date of birth'),
        ),
    ]
