# Generated by Django 5.1.4 on 2024-12-22 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0021_alter_attendance_date_alter_attendance_first_hour_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.IntegerField(choices=[(1, 'სტუდენტი'), (2, 'ლექტორი'), (3, 'ადმინისტრატორი'), (4, 'მენეჯერი'), (5, 'კურსდამთავრებული')], verbose_name='როლი'),
        ),
    ]
