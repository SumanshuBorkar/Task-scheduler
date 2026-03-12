"""
Tests for the health check endpoint.
"""
import pytest


@pytest.mark.django_db
class TestHealthCheck:

    def test_health_returns_200(self, api_client):
        """Health endpoint returns 200 when DB is reachable."""
        response = api_client.get('/api/health/')

        assert response.status_code == 200
        assert response.data['status'] == 'healthy'
        assert response.data['database'] == 'ok'

    def test_health_no_auth_required(self, api_client):
        """Health endpoint is publicly accessible."""
        # No credentials set on api_client
        response = api_client.get('/api/health/')
        assert response.status_code == 200