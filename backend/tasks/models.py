"""
Task domain models.
All models inherit BaseModel (UUID primary key + timestamps).
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

from core.models import BaseModel

User = get_user_model()


class TaskStatus(models.TextChoices):
    """
    Lifecycle states of a Task.
    A task moves through these states in order:
    PENDING → SCHEDULED → RUNNING → COMPLETED
                                  ↘ FAILED (after max retries)
    CANCELLED can happen from PENDING or SCHEDULED.
    """
    PENDING   = 'PENDING',   'Pending'
    SCHEDULED = 'SCHEDULED', 'Scheduled'
    RUNNING   = 'RUNNING',   'Running'
    COMPLETED = 'COMPLETED', 'Completed'
    FAILED    = 'FAILED',    'Failed'
    CANCELLED = 'CANCELLED', 'Cancelled'


class TaskPriority(models.TextChoices):
    """
    Execution priority. Higher priority tasks are
    picked up by the worker before lower priority ones.
    """
    LOW      = 'LOW',      'Low'
    NORMAL   = 'NORMAL',   'Normal'
    HIGH     = 'HIGH',     'High'
    CRITICAL = 'CRITICAL', 'Critical'


class Task(BaseModel):
    """
    Represents a unit of work scheduled by a user.

    Inherits from BaseModel:
      - id (UUID, primary key)
      - created_at (auto set on creation)
      - updated_at (auto updated on every save)
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,       # Delete tasks when user is deleted
        related_name='tasks',
        db_index=True,
        help_text="The user who owns this task."
    )
    title = models.CharField(
        max_length=255,
        help_text="Short description of what this task does."
    )
    description = models.TextField(
        blank=True,
        default='',
        help_text="Optional longer description."
    )
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.PENDING,
        db_index=True,                  # We filter by status very frequently
        help_text="Current lifecycle state of this task."
    )
    priority = models.CharField(
        max_length=10,
        choices=TaskPriority.choices,
        default=TaskPriority.NORMAL,
        db_index=True,
        help_text="Execution priority."
    )
    scheduled_at = models.DateTimeField(
        db_index=True,                  # Worker queries: WHERE scheduled_at <= NOW()
        help_text="When this task should be executed."
    )
    executed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When execution actually started."
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When execution finished (success or final failure)."
    )
    retry_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of execution attempts so far."
    )
    max_retries = models.PositiveIntegerField(
        default=3,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Maximum number of retry attempts before marking as FAILED."
    )
    # Stores the Celery task ID so we can track/revoke it
    celery_task_id = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Celery async task ID for tracking."
    )

    class Meta:
        db_table = 'tasks'
        ordering = ['-created_at']
        indexes = [
            # Composite index: worker query pattern is always
            # "give me PENDING/SCHEDULED tasks ordered by scheduled_at"
            models.Index(
                fields=['status', 'scheduled_at'],
                name='idx_task_status_scheduled'
            ),
            # User's task list is always filtered by user + ordered by created_at
            models.Index(
                fields=['user', '-created_at'],
                name='idx_task_user_created'
            ),
        ]

    def __str__(self):
        return f"{self.title} [{self.status}]"

    @property
    def can_retry(self) -> bool:
        """Returns True if this task has remaining retry attempts."""
        return self.retry_count < self.max_retries

    @property
    def is_terminal(self) -> bool:
        """Returns True if the task has reached a final state."""
        return self.status in (
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
        )


class TaskExecution(BaseModel):
    """
    Records a single execution attempt of a Task.
    One Task can have multiple TaskExecution records (one per retry).
    This gives us a full retry history per task.
    """

    class Outcome(models.TextChoices):
        SUCCESS = 'SUCCESS', 'Success'
        FAILURE = 'FAILURE', 'Failure'
        TIMEOUT = 'TIMEOUT', 'Timeout'

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='executions',
        db_index=True,
        help_text="The task this execution belongs to."
    )
    started_at = models.DateTimeField(
        help_text="When this execution attempt started."
    )
    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this execution attempt finished."
    )
    outcome = models.CharField(
        max_length=10,
        choices=Outcome.choices,
        help_text="Result of this execution attempt."
    )
    error_message = models.TextField(
        blank=True,
        default='',
        help_text="Error traceback or message if this attempt failed."
    )
    duration_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="How long this execution took in milliseconds."
    )
    worker_id = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Identifier of the Celery worker that ran this execution."
    )

    class Meta:
        db_table = 'task_executions'
        ordering = ['-started_at']

    def __str__(self):
        return f"Execution of {self.task.title} → {self.outcome}"


class TaskLog(BaseModel):
    """
    Append-only log messages generated during task execution.
    Useful for debugging failed tasks.
    """

    class Level(models.TextChoices):
        INFO    = 'INFO',    'Info'
        WARNING = 'WARNING', 'Warning'
        ERROR   = 'ERROR',   'Error'

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='logs',
        db_index=True,
        help_text="The task this log entry belongs to."
    )
    message = models.TextField(
        help_text="Log message content."
    )
    level = models.CharField(
        max_length=10,
        choices=Level.choices,
        default=Level.INFO,
        help_text="Severity level of this log entry."
    )

    class Meta:
        db_table = 'task_logs'
        ordering = ['created_at']   # Logs shown oldest-first (chronological)

    def __str__(self):
        return f"[{self.level}] {self.task.title}: {self.message[:50]}"