"""
Celery application factory.
This module creates the Celery app instance and configures it from Django settings.
It must be imported by Django at startup — handled via authentication/apps.py.
"""
import os
from celery import Celery

# Tell Celery which Django settings module to use
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Create the Celery application instance
# 'workers' is the name of this Celery app
celery_app = Celery('workers')

# Load all Celery config from Django settings keys that start with CELERY_
# namespace='CELERY' means CELERY_BROKER_URL → broker_url internally
celery_app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover @shared_task decorated functions in all installed apps
# Looks for a tasks.py in every app listed in INSTALLED_APPS
celery_app.autodiscover_tasks()


@celery_app.task(bind=True, ignore_result=True)
def debug_task(self):
    """
    Built-in diagnostic task.
    Call this to verify Celery is running: debug_task.delay()
    """
    print(f'Request: {self.request!r}')