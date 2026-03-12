"""
Tests for Task model properties and behavior.
"""
import pytest
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task, TaskStatus, TaskPriority


@pytest.mark.django_db
class TestTaskModel:

    def test_task_creation(self, test_user):
        """Task is created with correct defaults."""
        task = Task.objects.create(
            user=test_user,
            title='Test Task',
            scheduled_at=timezone.now() + timedelta(hours=1),
        )

        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.NORMAL
        assert task.retry_count == 0
        assert task.max_retries == 3
        assert task.id is not None       # UUID assigned
        assert task.created_at is not None

    def test_can_retry_true(self, test_user):
        """can_retry is True when retry_count < max_retries."""
        task = Task.objects.create(
            user=test_user,
            title='Test',
            scheduled_at=timezone.now() + timedelta(hours=1),
            retry_count=1,
            max_retries=3,
        )
        assert task.can_retry is True

    def test_can_retry_false(self, test_user):
        """can_retry is False when retry_count equals max_retries."""
        task = Task.objects.create(
            user=test_user,
            title='Test',
            scheduled_at=timezone.now() + timedelta(hours=1),
            retry_count=3,
            max_retries=3,
        )
        assert task.can_retry is False

    def test_is_terminal_completed(self, test_user):
        """COMPLETED status is terminal."""
        task = Task.objects.create(
            user=test_user,
            title='Test',
            scheduled_at=timezone.now() + timedelta(hours=1),
            status=TaskStatus.COMPLETED,
        )
        assert task.is_terminal is True

    def test_is_terminal_pending(self, test_user):
        """PENDING status is not terminal."""
        task = Task.objects.create(
            user=test_user,
            title='Test',
            scheduled_at=timezone.now() + timedelta(hours=1),
            status=TaskStatus.PENDING,
        )
        assert task.is_terminal is False