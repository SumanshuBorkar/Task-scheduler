"""
Tests for Tasks API endpoints.
"""
import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task, TaskStatus


def make_task(user, title='Test Task', hours_ahead=1, status=TaskStatus.PENDING):
    """Helper to create a task in the test database."""
    return Task.objects.create(
        user=user,
        title=title,
        scheduled_at=timezone.now() + timedelta(hours=hours_ahead),
        status=status,
    )


@pytest.mark.django_db
class TestTaskListCreate:

    def test_list_tasks_authenticated(self, auth_client, test_user):
        """Authenticated user can list their tasks."""
        make_task(test_user, 'Task 1')
        make_task(test_user, 'Task 2')

        response = auth_client.get('/api/tasks/')

        assert response.status_code == 200
        assert response.data['count'] == 2

    def test_list_tasks_only_own(self, auth_client, test_user, test_user_2):
        """User only sees their own tasks, not other users' tasks."""
        make_task(test_user, 'My Task')
        make_task(test_user_2, 'Their Task')

        response = auth_client.get('/api/tasks/')

        assert response.status_code == 200
        assert response.data['count'] == 1
        assert response.data['results'][0]['title'] == 'My Task'

    def test_list_tasks_unauthenticated(self, api_client):
        """Unauthenticated request returns 401."""
        response = api_client.get('/api/tasks/')
        assert response.status_code == 401

    def test_create_task_success(self, auth_client):
        """Valid task creation returns 201."""
        payload = {
            'title': 'New Task',
            'scheduled_at': (
                timezone.now() + timedelta(hours=2)
            ).isoformat(),
            'priority': 'HIGH',
        }
        response = auth_client.post('/api/tasks/', payload, format='json')

        assert response.status_code == 201
        assert response.data['success'] is True
        assert response.data['task']['title'] == 'New Task'
        assert response.data['task']['status'] == 'PENDING'

    def test_create_task_past_scheduled_at(self, auth_client):
        """Task scheduled in the past returns 400."""
        payload = {
            'title': 'Past Task',
            'scheduled_at': (
                timezone.now() - timedelta(hours=1)
            ).isoformat(),
        }
        response = auth_client.post('/api/tasks/', payload, format='json')

        assert response.status_code == 400

    def test_create_task_missing_title(self, auth_client):
        """Missing title returns 400."""
        payload = {
            'scheduled_at': (
                timezone.now() + timedelta(hours=1)
            ).isoformat(),
        }
        response = auth_client.post('/api/tasks/', payload, format='json')

        assert response.status_code == 400


@pytest.mark.django_db
class TestTaskRetrieveUpdateDelete:

    def test_retrieve_own_task(self, auth_client, test_user):
        """User can retrieve their own task."""
        task = make_task(test_user)
        response = auth_client.get(f'/api/tasks/{task.id}/')

        assert response.status_code == 200
        assert response.data['task']['id'] == str(task.id)

    def test_retrieve_other_users_task(self, auth_client, test_user_2):
        """User cannot retrieve another user's task."""
        task = make_task(test_user_2)
        response = auth_client.get(f'/api/tasks/{task.id}/')

        assert response.status_code == 404

    def test_delete_own_task(self, auth_client, test_user):
        """User can delete their own PENDING task."""
        task = make_task(test_user)
        response = auth_client.delete(f'/api/tasks/{task.id}/')

        assert response.status_code == 204
        assert not Task.objects.filter(id=task.id).exists()

    def test_delete_running_task_forbidden(self, auth_client, test_user):
        """Cannot delete a RUNNING task."""
        task = make_task(test_user, status=TaskStatus.RUNNING)
        response = auth_client.delete(f'/api/tasks/{task.id}/')

        assert response.status_code == 400


@pytest.mark.django_db
class TestTaskActions:

    def test_complete_pending_task(self, auth_client, test_user):
        """User can manually complete a PENDING task."""
        task = make_task(test_user)
        response = auth_client.post(f'/api/tasks/{task.id}/complete/')

        assert response.status_code == 200
        assert response.data['task']['status'] == 'COMPLETED'

        task.refresh_from_db()
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None

    def test_complete_already_completed_task(self, auth_client, test_user):
        """Cannot complete an already completed task."""
        task = make_task(test_user, status=TaskStatus.COMPLETED)
        response = auth_client.post(f'/api/tasks/{task.id}/complete/')

        assert response.status_code == 400

    def test_cancel_pending_task(self, auth_client, test_user):
        """User can cancel a PENDING task."""
        task = make_task(test_user)
        response = auth_client.post(f'/api/tasks/{task.id}/cancel/')

        assert response.status_code == 200
        assert response.data['task']['status'] == 'CANCELLED'

    def test_cancel_running_task_forbidden(self, auth_client, test_user):
        """Cannot cancel a RUNNING task."""
        task = make_task(test_user, status=TaskStatus.RUNNING)
        response = auth_client.post(f'/api/tasks/{task.id}/cancel/')

        assert response.status_code == 400

    def test_filter_tasks_by_status(self, auth_client, test_user):
        """Tasks can be filtered by status query param."""
        make_task(test_user, 'Pending Task', status=TaskStatus.PENDING)
        make_task(test_user, 'Completed Task', status=TaskStatus.COMPLETED)

        response = auth_client.get('/api/tasks/?status=PENDING')

        assert response.status_code == 200
        assert response.data['count'] == 1
        assert response.data['results'][0]['title'] == 'Pending Task'