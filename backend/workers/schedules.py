"""
Celery Beat periodic task schedule.
Defines the poll_and_dispatch_due_tasks beat task that
checks for due tasks every 60 seconds.
"""
from celery.schedules import crontab


CELERY_BEAT_SCHEDULE = {
    'poll-and-dispatch-due-tasks': {
        # The Celery task to call
        'task': 'workers.tasks.poll_and_dispatch_due_tasks',
        # Run every 60 seconds
        'schedule': 60.0,
    },
}