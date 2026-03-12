"""
This module ensures the Celery app is loaded when Django starts,
so that the @shared_task decorator works correctly across all apps.
"""
from .celery import celery_app

__all__ = ('celery_app',)