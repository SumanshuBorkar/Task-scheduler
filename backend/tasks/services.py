"""
Services: all business logic for the tasks domain.
Each function represents one business operation.
"""
import logging
from django.utils import timezone
from core.exceptions import ServiceError, NotFoundError, PermissionError
from .models import Task, TaskStatus, TaskPriority
from .selectors import get_task_for_user

logger = logging.getLogger(__name__)


def create_task(user, title, description='', scheduled_at=None,
                priority=TaskPriority.NORMAL, max_retries=3):
    """
    Create a new scheduled task for a user.
    Validates that scheduled_at is in the future.
    """
    if not scheduled_at:
        raise ServiceError("scheduled_at is required.")

    if scheduled_at <= timezone.now():
        raise ServiceError("Scheduled time must be in the future.")

    task = Task.objects.create(
        user=user,
        title=title,
        description=description,
        scheduled_at=scheduled_at,
        priority=priority,
        max_retries=max_retries,
        status=TaskStatus.PENDING,
    )

    logger.info(f"Task created: {task.id} by user {user.email}")
    return task


def complete_task(task_id, user):
    """
    Manually mark a task as completed by the user.
    Only allowed if the task is not already in a terminal state.
    """
    task = get_task_for_user(task_id, user)

    if not task:
        raise NotFoundError("Task not found.")

    if task.is_terminal:
        raise ServiceError(
            f"Task is already {task.status} and cannot be modified."
        )

    task.status = TaskStatus.COMPLETED
    task.completed_at = timezone.now()
    task.save(update_fields=['status', 'completed_at', 'updated_at'])

    logger.info(f"Task manually completed: {task.id} by user {user.email}")
    return task


def cancel_task(task_id, user):
    """
    Cancel a task that hasn't started executing yet.
    Cannot cancel tasks that are RUNNING, COMPLETED, or FAILED.
    """
    task = get_task_for_user(task_id, user)

    if not task:
        raise NotFoundError("Task not found.")

    if task.status == TaskStatus.RUNNING:
        raise ServiceError("Cannot cancel a task that is currently running.")

    if task.is_terminal:
        raise ServiceError(
            f"Task is already {task.status} and cannot be cancelled."
        )

    # Revoke the Celery task if it was already queued
    if task.celery_task_id:
        try:
            from celery.app.control import Control
            from workers.celery import celery_app
            celery_app.control.revoke(task.celery_task_id, terminate=False)
        except Exception as e:
            # Log but don't fail — the task state change is more important
            logger.warning(f"Could not revoke Celery task {task.celery_task_id}: {e}")

    task.status = TaskStatus.CANCELLED
    task.completed_at = timezone.now()
    task.save(update_fields=['status', 'completed_at', 'updated_at'])

    logger.info(f"Task cancelled: {task.id} by user {user.email}")
    return task


def update_task(task_id, user, **kwargs):
    """
    Update allowed fields on a task.
    Only possible if the task is still PENDING.
    """
    task = get_task_for_user(task_id, user)

    if not task:
        raise NotFoundError("Task not found.")

    if task.status != TaskStatus.PENDING:
        raise ServiceError(
            "Only PENDING tasks can be edited."
        )

    allowed_fields = {'title', 'description', 'scheduled_at', 'priority', 'max_retries'}
    update_fields = ['updated_at']

    for field, value in kwargs.items():
        if field in allowed_fields:
            if field == 'scheduled_at' and value <= timezone.now():
                raise ServiceError("Scheduled time must be in the future.")
            setattr(task, field, value)
            update_fields.append(field)

    task.save(update_fields=update_fields)
    return task