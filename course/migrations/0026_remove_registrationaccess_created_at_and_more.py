# Generated by Django 5.1.4 on 2024-12-17 08:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0025_registrationaccess'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registrationaccess',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='registrationaccess',
            name='updated_at',
        ),
    ]
