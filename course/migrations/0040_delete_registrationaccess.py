# Generated by Django 5.1.4 on 2024-12-19 16:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0039_graderecord_created_at_graderecord_updated_at'),
    ]

    operations = [
        migrations.DeleteModel(
            name='RegistrationAccess',
        ),
    ]