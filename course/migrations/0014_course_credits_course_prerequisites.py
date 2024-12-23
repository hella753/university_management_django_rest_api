# Generated by Django 5.1.4 on 2024-12-11 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0013_resource_lecture_syllabus_lecture_resources'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='credits',
            field=models.PositiveSmallIntegerField(default=5, verbose_name='Credits'),
        ),
        migrations.AddField(
            model_name='course',
            name='prerequisites',
            field=models.ManyToManyField(blank=True, to='course.course', verbose_name='Prerequisites'),
        ),
    ]
