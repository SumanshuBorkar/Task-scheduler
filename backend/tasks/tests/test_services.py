"""
Tests for the tasks service layer.
Tests business logic in isolation from HTTP.
"""
import pytest
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task, TaskStatus
from tasks import services
from core.exceptions import ServiceError, NotFoundError


@pytest.mark.django_db
class TestCreateTask:

    def test_create_task_success(self, test_user, future_datetime):
        """Service creates task with correct fields."""
        task = services.create_task(
            user=test_user,
            title='My Task',
            scheduled_at=future_datetime,
        )

        assert task.id is not None
        assert task.title == 'My Task'
        assert task.user == test_user
        assert task.status == TaskStatus.PENDING

    def test_create_task_past_time_raises(self, test_user, past_datetime):
        """Creating a task in the past raises ServiceError."""
        with pytest.raises(ServiceError, match="future"):
            services.create_task(
                user=test_user,
                title='Past Task',
                scheduled_at=past_datetime,
            )

    def test_create_task_no_scheduled_at_raises(self, test_user):
        """Missing scheduled_at raises ServiceError."""
        with pytest.raises(ServiceError):
            services.create_task(user=test_user, title='No Time')


@pytest.mark.django_db
class TestCompleteTask:

    def test_complete_pending_task(self, test_user, future_datetime):
        """Completing a PENDING task sets status to COMPLETED."""
        task = Task.objects.create(
            user=test_user,
            title='Test',
            scheduled_at=future_datetime,
        )
        result = services.complete_task(task.id, test_user)

        assert result.status == TaskStatus.COMPLETED
        assert result.completed_at is not None

    def test_complete_nonexistent_task_raises(self, test_user):
        """Completing a non-existent task raises NotFoundError."""
        import uuid
        with pytest.raises(NotFoundError):
            services.complete_task(uuid.uuid4(), test_user)

    def test_complete_already_terminal_raises(self, test_user, future_datetime):
        """Completing an already-completed task raises ServiceError."""
        task = Task.objects.create(
            user=test_user,
            title='Test',
            scheduled_at=future_datetime,
            status=TaskStatus.COMPLETED,
        )
        with pytest.raises(ServiceError):
            services.complete_task(task.id, test_user)


@pytest.mark.django_db
class TestCancelTask:

    def test_cancel_pending_task(self, test_user, future_datetime):
        """Cancelling a PENDING task sets status to CANCELLED."""
        task = Task.objects.create(
            user=test_user,
            title='Test',
            scheduled_at=future_datetime,
        )
        result = services.cancel_task(task.id, test_user)

        assert result.status == TaskStatus.CANCELLED

    def test_cancel_running_task_raises(self, test_user, future_datetime):
        """Cancelling a RUNNING task raises ServiceError."""
        task = Task.objects.create(
            user=test_user,
            title='Test',
            scheduled_at=future_datetime,
            status=TaskStatus.RUNNING,
        )
        with pytest.raises(ServiceError, match="running"):
            services.cancel_task(task.id, test_user)