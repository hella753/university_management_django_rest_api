# Generated by Django 5.1.4 on 2024-12-09 18:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Department name')),
                ('code', models.CharField(max_length=10, verbose_name='Department code')),
            ],
        ),
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Faculty name')),
                ('code', models.CharField(max_length=10, verbose_name='Faculty code')),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Course name')),
                ('code', models.CharField(max_length=10, verbose_name='Course code')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.department', verbose_name='Department')),
            ],
        ),
        migrations.AddField(
            model_name='department',
            name='faculty',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.faculty', verbose_name='Faculty'),
        ),
        migrations.CreateModel(
            name='Lecture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Lecture name')),
                ('day', models.CharField(max_length=10, verbose_name='Day')),
                ('time', models.TimeField(verbose_name='Time')),
                ('location', models.CharField(max_length=50, verbose_name='Location')),
                ('year', models.PositiveSmallIntegerField(verbose_name='Year')),
                ('is_full', models.BooleanField(default=False, verbose_name='Is full')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.course', verbose_name='Course')),
                ('professor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Professor')),
            ],
        ),
    ]
