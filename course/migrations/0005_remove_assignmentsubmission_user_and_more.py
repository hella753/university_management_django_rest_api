# Generated by Django 5.1.4 on 2024-12-09 19:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0004_remove_grade_user_grade_student'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignmentsubmission',
            name='user',
        ),
        migrations.AddField(
            model_name='assignmentsubmission',
            name='student',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Student'),
            preserve_default=False,
        ),
    ]