# Generated by Django 5.1.4 on 2024-12-19 20:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0043_alter_grade_grade_alter_graderecord_grade'),
        ('user', '0018_remove_user_telephone_user_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='course.department', verbose_name='Department'),
        ),
    ]
