from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uni_backend.settings')

import django
django.setup()

app = Celery('uni_backend')

app.conf.enable_utc = False

app.conf.update(timezone = 'Asia/Tbilisi')

app.config_from_object(settings, namespace='CELERY')

app.conf.beat_schedule = {
    'deactivate-student-status': {
        'task': 'user.tasks.deactivate_student_status',
        # Deactivates student status of students who have loan on January 1 and June 1
        'schedule': crontab(hour=0, minute=0, day_of_month="1,6", month_of_year=1),
    },
    'make-graduate': {
        'task': 'user.tasks.make_graduate',
        # Add students who graduated to the graduates group on January 1
        'schedule': crontab(hour=0, minute=0, day_of_month=1, month_of_year=1),
    }
}

app.autodiscover_tasks()
