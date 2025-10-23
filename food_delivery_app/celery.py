"""
Celery configuration for food_delivery_app project.
"""
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_delivery_app.settings')

app = Celery('food_delivery_app')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print(f'Request: {self.request!r}')


# Celery Beat Schedule (for periodic tasks)
app.conf.beat_schedule = {
    # Example: Clean up expired OTPs every hour
    'cleanup-expired-otps': {
        'task': 'core.tasks.cleanup_expired_otps',
        'schedule': crontab(minute=0),  # Every hour
    },
    # Example: Send booking reminders
    # 'send-booking-reminders': {
    #     'task': 'core.tasks.send_booking_reminders',
    #     'schedule': crontab(minute='*/30'),  # Every 30 minutes
    # },
}

# Task routing (optional - for advanced queue management)
app.conf.task_routes = {
    'core.tasks.send_sms': {'queue': 'sms'},
    'core.tasks.send_email': {'queue': 'email'},
    'core.tasks.*': {'queue': 'default'},
}

