# Generated by Django 5.1.4 on 2024-12-22 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0047_assignment_description_en_assignment_description_ka_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lecture',
            name='day',
            field=models.IntegerField(blank=True, choices=[(1, 'ორშაბათი'), (2, 'სამშაბათი'), (3, 'ოთხშაბათი'), (4, 'ხუთშაბათი'), (5, 'პარასკევი'), (6, 'შაბათი'), (7, 'კვირა')], null=True, verbose_name='დღე'),
        ),
        migrations.AlterField(
            model_name='lecture',
            name='day_en',
            field=models.IntegerField(blank=True, choices=[(1, 'ორშაბათი'), (2, 'სამშაბათი'), (3, 'ოთხშაბათი'), (4, 'ხუთშაბათი'), (5, 'პარასკევი'), (6, 'შაბათი'), (7, 'კვირა')], null=True, verbose_name='დღე'),
        ),
        migrations.AlterField(
            model_name='lecture',
            name='day_ka',
            field=models.IntegerField(blank=True, choices=[(1, 'ორშაბათი'), (2, 'სამშაბათი'), (3, 'ოთხშაბათი'), (4, 'ხუთშაბათი'), (5, 'პარასკევი'), (6, 'შაბათი'), (7, 'კვირა')], null=True, verbose_name='დღე'),
        ),
    ]
