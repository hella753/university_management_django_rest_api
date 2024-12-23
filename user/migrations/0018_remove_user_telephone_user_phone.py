# Generated by Django 5.1.4 on 2024-12-19 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0017_user_role'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='telephone',
        ),
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, max_length=11, null=True, verbose_name='Phone'),
        ),
    ]