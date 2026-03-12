"""
Tests for Celery worker task execution logic.
Uses eager execution (CELERY_TASK_ALWAYS_EAGER) so tasks
run synchronously in the test process — no worker needed.
"""
import pytest
from unittest.mock import patch
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task, TaskStatus, TaskExecution, TaskLog


def make_due_task(user, title='Test Task'):
    """Creates a task with scheduled_at in the past (immediately due)."""
    return Task.objects.create(
        user=user,
        title=title,
        scheduled_at=timezone.now() - timedelta(minutes=5),
        status=TaskStatus.PENDING,
    )


@pytest.mark.django_db
class TestExecuteTask:

    @pytest.fixture(autouse=True)
    def eager_celery(self, settings):
        """
        Force Celery to run tasks synchronously during tests.
        Without this, tasks would be queued but never executed in tests.
        """
        settings.CELERY_TASK_ALWAYS_EAGER = True
        settings.CELERY_TASK_EAGER_PROPAGATES = True

    def test_task_completes_successfully(self, test_user):
        """execute_task marks task as COMPLETED on success."""
        from workers.tasks import execute_task

        task = make_due_task(test_user)

        # Patch _run_task_logic to avoid the time.sleep(2) in tests
        with patch('workers.tasks._run_task_logic'):
            execute_task(str(task.id))

        task.refresh_from_db()
        assert task.status == TaskStatus.COMPLETED
        assert task.executed_at is not None
        assert task.completed_at is not None

        # Verify execution record was created
        assert TaskExecution.objects.filter(
            task=task,
            outcome=TaskExecution.Outcome.SUCCESS
        ).exists()

    def test_task_creates_success_log(self, test_user):
        """Successful execution creates INFO log entries."""
        from workers.tasks import execute_task

        task = make_due_task(test_user)

        with patch('workers.tasks._run_task_logic'):
            execute_task(str(task.id))

        logs = TaskLog.objects.filter(task=task)
        assert logs.exists()
        assert logs.filter(level='INFO').exists()

    def test_task_nonexistent_id_does_not_crash(self):
        """execute_task with a non-existent task ID exits gracefully."""
        from workers.tasks import execute_task
        import uuid

        # Should not raise any exception
        execute_task(str(uuid.uuid4()))

    def test_task_skips_terminal_status(self, test_user):
        """execute_task skips tasks already in a terminal state."""
        from workers.tasks import execute_task

        task = make_due_task(test_user)
        task.status = TaskStatus.COMPLETED
        task.save()

        with patch('workers.tasks._run_task_logic') as mock_logic:
            execute_task(str(task.id))

        # Logic should never have been called
        mock_logic.assert_not_called()


@pytest.mark.django_db
class TestPollAndDispatch:

    def test_dispatches_due_tasks(self, test_user):
        """poll_and_dispatch_due_tasks dispatches all due tasks."""
        from workers.tasks import poll_and_dispatch_due_tasks

        due_task = make_due_task(test_user, 'Due Task')
        future_task = Task.objects.create(
            user=test_user,
            title='Future Task',
            scheduled_at=timezone.now() + timedelta(hours=2),
            status=TaskStatus.PENDING,
        )

        with patch('workers.tasks.execute_task.apply_async') as mock_dispatch:
            mock_dispatch.return_value.id = 'fake-celery-id'
            count = poll_and_dispatch_due_tasks()

        assert count == 1

        due_task.refresh_from_db()
        assert due_task.status == TaskStatus.SCHEDULED

        future_task.refresh_from_db()
        assert future_task.status == TaskStatus.PENDING