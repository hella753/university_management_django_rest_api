# Generated by Django 5.1.4 on 2024-12-16 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0013_remove_user_university_scholarship_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(blank=True, choices=[('student', 'Student'), ('professor', 'Professor'), ('manager', 'Manager'), ('alumni', 'Alumni')], max_length=10, null=True),
        ),
    ]