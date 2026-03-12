"""
Celery task definitions.
These are the functions that run inside the Celery worker process.
"""
import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,      # Base retry delay in seconds
    name='workers.tasks.execute_task',
)
def execute_task(self, task_id: str):
    """
    Core task execution function.

    Called by Celery Beat when a task's scheduled_at time is reached.
    Handles the full lifecycle: RUNNING → COMPLETED or FAILED with retries.

    bind=True gives us access to `self` (the Celery task instance),
    which we need to call self.retry() for retry logic.
    """
    # Import here to avoid circular imports at module load time
    from tasks.models import Task, TaskStatus, TaskExecution, TaskLog

    logger.info(f"[execute_task] Starting execution for task_id={task_id}")

    # ── Fetch the Task ────────────────────────────────────────────────────────
    try:
        task = Task.objects.select_related('user').get(id=task_id)
    except Task.DoesNotExist:
        logger.error(f"[execute_task] Task {task_id} not found. Aborting.")
        return

    # ── Guard: skip if already in a terminal state ────────────────────────────
    if task.is_terminal:
        logger.warning(
            f"[execute_task] Task {task_id} is already {task.status}. Skipping."
        )
        return

    # ── Mark as RUNNING ───────────────────────────────────────────────────────
    started_at = timezone.now()
    task.status = TaskStatus.RUNNING
    task.executed_at = started_at
    task.save(update_fields=['status', 'executed_at', 'updated_at'])

    TaskLog.objects.create(
        task=task,
        level='INFO',
        message=f"Execution started. Attempt {task.retry_count + 1} of {task.max_retries + 1}."
    )

    # ── Execute the task logic ────────────────────────────────────────────────
    try:
        _run_task_logic(task)

        # ── Success path ──────────────────────────────────────────────────────
        finished_at = timezone.now()
        duration_ms = int((finished_at - started_at).total_seconds() * 1000)

        task.status = TaskStatus.COMPLETED
        task.completed_at = finished_at
        task.save(update_fields=['status', 'completed_at', 'updated_at'])

        TaskExecution.objects.create(
            task=task,
            started_at=started_at,
            finished_at=finished_at,
            outcome=TaskExecution.Outcome.SUCCESS,
            duration_ms=duration_ms,
            worker_id=self.request.hostname or 'unknown',
        )

        TaskLog.objects.create(
            task=task,
            level='INFO',
            message=f"Execution completed successfully in {duration_ms}ms."
        )

        logger.info(f"[execute_task] Task {task_id} completed in {duration_ms}ms.")

    except Exception as exc:
        # ── Failure path ──────────────────────────────────────────────────────
        finished_at = timezone.now()
        duration_ms = int((finished_at - started_at).total_seconds() * 1000)
        error_message = str(exc)

        logger.error(
            f"[execute_task] Task {task_id} failed on attempt "
            f"{task.retry_count + 1}: {error_message}"
        )

        TaskLog.objects.create(
            task=task,
            level='ERROR',
            message=f"Attempt {task.retry_count + 1} failed: {error_message}"
        )

        TaskExecution.objects.create(
            task=task,
            started_at=started_at,
            finished_at=finished_at,
            outcome=TaskExecution.Outcome.FAILURE,
            error_message=error_message,
            duration_ms=duration_ms,
            worker_id=self.request.hostname or 'unknown',
        )

        # ── Retry or fail permanently ─────────────────────────────────────────
        task.retry_count += 1

        if task.can_retry:
            # Exponential backoff: 60s, 120s, 240s...
            retry_delay = 60 * (2 ** (task.retry_count - 1))

            task.status = TaskStatus.PENDING
            task.save(update_fields=['status', 'retry_count', 'updated_at'])

            TaskLog.objects.create(
                task=task,
                level='WARNING',
                message=(
                    f"Scheduling retry {task.retry_count} of {task.max_retries} "
                    f"in {retry_delay}s."
                )
            )

            logger.info(
                f"[execute_task] Retrying task {task_id} in {retry_delay}s "
                f"(attempt {task.retry_count}/{task.max_retries})."
            )

            # Schedule the retry via Celery's built-in retry mechanism
            raise self.retry(exc=exc, countdown=retry_delay)

        else:
            # Max retries exceeded — mark as permanently failed
            task.status = TaskStatus.FAILED
            task.completed_at = finished_at
            task.save(update_fields=[
                'status', 'retry_count', 'completed_at', 'updated_at'
            ])

            TaskLog.objects.create(
                task=task,
                level='ERROR',
                message=(
                    f"Task permanently failed after {task.retry_count} attempts."
                )
            )

            logger.error(
                f"[execute_task] Task {task_id} permanently failed "
                f"after {task.retry_count} attempts."
            )


def _run_task_logic(task):
    """
    The actual work performed when a task executes.

    In a real system this would dispatch to different handlers
    based on task type (send email, generate report, etc).
    For now it simulates work and logs what it's doing.

    Raises an exception to simulate failure — useful for testing retry logic.
    """
    import time

    logger.info(
        f"[_run_task_logic] Running task '{task.title}' "
        f"for user {task.user.email}"
    )

    # Simulate task work taking some time
    time.sleep(2)

    # Uncomment the line below to test retry/failure logic:
    # raise Exception("Simulated task failure for testing retry logic")

    logger.info(f"[_run_task_logic] Task '{task.title}' logic completed.")


@shared_task(name='workers.tasks.poll_and_dispatch_due_tasks')
def poll_and_dispatch_due_tasks():
    """
    Periodic task called by Celery Beat every 60 seconds.
    Finds all tasks due for execution and dispatches them to the worker queue.

    This is the bridge between the Django database and Celery workers:
    - Beat calls this every 60s
    - This queries the DB for due tasks
    - Dispatches each one as an individual execute_task job
    """
    from tasks.selectors import get_pending_due_tasks

    due_tasks = get_pending_due_tasks()
    dispatched = 0

    for task in due_tasks:
        # Mark as SCHEDULED so Beat doesn't pick it up again next cycle
        task.status = 'SCHEDULED'
        task.save(update_fields=['status', 'updated_at'])

        # Dispatch to the worker queue
        result = execute_task.apply_async(
            args=[str(task.id)],
            queue='default',
        )

        # Store the Celery task ID for tracking/revocation
        task.celery_task_id = result.id
        task.save(update_fields=['celery_task_id', 'updated_at'])

        dispatched += 1
        logger.info(
            f"[poll_and_dispatch] Dispatched task {task.id} "
            f"('{task.title}') → Celery job {result.id}"
        )

    logger.info(f"[poll_and_dispatch] Cycle complete. Dispatched {dispatched} tasks.")
    return dispatched