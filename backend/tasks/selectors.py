"""
Selectors: all database READ operations for the tasks domain.
Views and services import from here — never query Task.objects directly elsewhere.
"""
from django.utils import timezone
from .models import Task, TaskStatus


def get_tasks_for_user(user, filters=None):
    """
    Return all tasks belonging to a user.
    Optionally filter by status, priority, or search term.
    """
    queryset = (
        Task.objects
        .filter(user=user)
        .select_related('user')         # Avoids extra query when accessing task.user
        .prefetch_related('executions', 'logs')
    )

    if not filters:
        return queryset

    status = filters.get('status')
    priority = filters.get('priority')
    search = filters.get('search')

    if status:
        queryset = queryset.filter(status=status)
    if priority:
        queryset = queryset.filter(priority=priority)
    if search:
        queryset = queryset.filter(title__icontains=search)

    return queryset


def get_task_for_user(task_id, user):
    """
    Return a single task by ID, ensuring it belongs to the requesting user.
    Returns None if not found or not owned by user.
    """
    try:
        return Task.objects.get(id=task_id, user=user)
    except Task.DoesNotExist:
        return None


def get_pending_due_tasks():
    """
    Return tasks that are due for execution right now.
    Called by the Celery Beat scheduler in Step 7.
    """
    return Task.objects.filter(
        status__in=[TaskStatus.PENDING, TaskStatus.SCHEDULED],
        scheduled_at__lte=timezone.now(),
    ).select_related('user')