# ledgerlink/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import importlib_metadata

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ledgerlink.settings')

app = Celery('ledgerlink')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

from celery.schedules import crontab

app.conf.beat_schedule = {
    'check-blob-for-orders-every-minute': {
        'task': 'billing.tasks.check_blob_for_orders',
        'schedule': crontab(minute='*/1'),  # Every minute
    },
}
