"""
Tests for authentication API endpoints.
Covers: registration, login, logout, profile retrieval.
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestRegisterView:

    def test_register_success(self, api_client):
        """Valid registration returns 201 with tokens."""
        url = reverse('auth-register')
        payload = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'Testpass123!',
            'password_confirm': 'Testpass123!',
        }
        response = api_client.post(url, payload, format='json')

        assert response.status_code == 201
        assert response.data['success'] is True
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
        assert User.objects.filter(email='new@example.com').exists()

    def test_register_duplicate_email(self, api_client, test_user):
        """Registration with existing email returns 400."""
        url = reverse('auth-register')
        payload = {
            'username': 'anotheruser',
            'email': 'test@example.com',   # already exists via test_user fixture
            'password': 'Testpass123!',
            'password_confirm': 'Testpass123!',
        }
        response = api_client.post(url, payload, format='json')

        assert response.status_code == 400
        assert response.data['success'] is False
        assert 'email' in response.data['errors']

    def test_register_password_mismatch(self, api_client):
        """Mismatched passwords return 400."""
        url = reverse('auth-register')
        payload = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'Testpass123!',
            'password_confirm': 'WrongPass123!',
        }
        response = api_client.post(url, payload, format='json')

        assert response.status_code == 400
        assert response.data['success'] is False

    def test_register_missing_fields(self, api_client):
        """Missing required fields return 400."""
        url = reverse('auth-register')
        response = api_client.post(url, {}, format='json')

        assert response.status_code == 400


@pytest.mark.django_db
class TestLoginView:

    def test_login_success(self, api_client, test_user):
        """Valid credentials return 200 with JWT tokens."""
        url = reverse('auth-login')
        payload = {
            'email': 'test@example.com',
            'password': 'Testpass123!',
        }
        response = api_client.post(url, payload, format='json')

        assert response.status_code == 200
        assert response.data['success'] is True
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']

    def test_login_wrong_password(self, api_client, test_user):
        """Wrong password returns 401."""
        url = reverse('auth-login')
        payload = {
            'email': 'test@example.com',
            'password': 'WrongPassword!',
        }
        response = api_client.post(url, payload, format='json')

        assert response.status_code == 401
        assert response.data['success'] is False

    def test_login_nonexistent_email(self, api_client):
        """Non-existent email returns 401."""
        url = reverse('auth-login')
        payload = {
            'email': 'nobody@example.com',
            'password': 'Testpass123!',
        }
        response = api_client.post(url, payload, format='json')

        assert response.status_code == 401


@pytest.mark.django_db
class TestMeView:

    def test_me_authenticated(self, auth_client, test_user):
        """Authenticated request returns user profile."""
        url = reverse('auth-me')
        response = auth_client.get(url)

        assert response.status_code == 200
        assert response.data['user']['email'] == test_user.email

    def test_me_unauthenticated(self, api_client):
        """Unauthenticated request returns 401."""
        url = reverse('auth-me')
        response = api_client.get(url)

        assert response.status_code == 401