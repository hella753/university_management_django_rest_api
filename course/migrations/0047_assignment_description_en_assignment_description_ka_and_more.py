# Generated by Django 5.1.4 on 2024-12-21 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0046_alter_assignment_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='description_en',
            field=models.TextField(blank=True, null=True, verbose_name='აღწერა'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='description_ka',
            field=models.TextField(blank=True, null=True, verbose_name='აღწერა'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='name_en',
            field=models.CharField(max_length=50, null=True, verbose_name='დავალების სახელი'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='name_ka',
            field=models.CharField(max_length=50, null=True, verbose_name='დავალების სახელი'),
        ),
        migrations.AddField(
            model_name='course',
            name='name_en',
            field=models.CharField(max_length=50, null=True, verbose_name='კურსის სახელი'),
        ),
        migrations.AddField(
            model_name='course',
            name='name_ka',
            field=models.CharField(max_length=50, null=True, verbose_name='კურსის სახელი'),
        ),
        migrations.AddField(
            model_name='department',
            name='name_en',
            field=models.CharField(max_length=50, null=True, verbose_name='დეპარტამენტის სახელი'),
        ),
        migrations.AddField(
            model_name='department',
            name='name_ka',
            field=models.CharField(max_length=50, null=True, verbose_name='დეპარტამენტის სახელი'),
        ),
        migrations.AddField(
            model_name='faculty',
            name='name_en',
            field=models.CharField(max_length=50, null=True, verbose_name='ფაკულტეტის სახელი'),
        ),
        migrations.AddField(
            model_name='faculty',
            name='name_ka',
            field=models.CharField(max_length=50, null=True, verbose_name='ფაკულტეტის სახელი'),
        ),
        migrations.AddField(
            model_name='lecture',
            name='day_en',
            field=models.IntegerField(blank=True, choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')], null=True, verbose_name='დღე'),
        ),
        migrations.AddField(
            model_name='lecture',
            name='day_ka',
            field=models.IntegerField(blank=True, choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')], null=True, verbose_name='დღე'),
        ),
        migrations.AddField(
            model_name='lecture',
            name='name_en',
            field=models.CharField(max_length=50, null=True, verbose_name='ლექციის სახელი'),
        ),
        migrations.AddField(
            model_name='lecture',
            name='name_ka',
            field=models.CharField(max_length=50, null=True, verbose_name='ლექციის სახელი'),
        ),
        migrations.AddField(
            model_name='resource',
            name='name_en',
            field=models.CharField(max_length=50, null=True, verbose_name='რესურსის სახელი'),
        ),
        migrations.AddField(
            model_name='resource',
            name='name_ka',
            field=models.CharField(max_length=50, null=True, verbose_name='რესურსის სახელი'),
        ),
    ]