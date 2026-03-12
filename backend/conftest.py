"""
Shared pytest fixtures available to all test files.
Place this file at the backend/ root so all apps can access these fixtures.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client():
    """
    Unauthenticated DRF API client.
    Use this for testing public endpoints like /register/ and /login/.
    """
    return APIClient()


@pytest.fixture
def test_user(db):
    """
    Creates a real user in the test database.
    The `db` fixture is provided by pytest-django and gives access
    to the database within a test.
    """
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='Testpass123!',
    )
    return user


@pytest.fixture
def test_user_2(db):
    """Second user — used for testing ownership/permission boundaries."""
    return User.objects.create_user(
        username='otheruser',
        email='other@example.com',
        password='Testpass123!',
    )


@pytest.fixture
def auth_client(test_user):
    """
    Authenticated DRF API client with a valid JWT access token.
    Use this for all endpoints that require IsAuthenticated.
    """
    client = APIClient()
    refresh = RefreshToken.for_user(test_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


@pytest.fixture
def auth_client_2(test_user_2):
    """Authenticated client for the second test user."""
    client = APIClient()
    refresh = RefreshToken.for_user(test_user_2)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


@pytest.fixture
def future_datetime():
    """Returns a datetime 1 hour in the future. Used for task scheduled_at."""
    from django.utils import timezone
    from datetime import timedelta
    return timezone.now() + timedelta(hours=1)


@pytest.fixture
def past_datetime():
    """Returns a datetime 1 hour in the past. Used for testing due task detection."""
    from django.utils import timezone
    from datetime import timedelta
    return timezone.now() - timedelta(hours=1)