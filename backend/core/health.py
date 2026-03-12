"""
Health check endpoint.
Used by Docker healthchecks, load balancers, and monitoring tools
to verify the service is running and can reach the database.
"""
from django.db import connection
from django.db.utils import OperationalError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    GET /api/health/
    Returns 200 if the service is healthy, 503 if the database is unreachable.
    No authentication required — monitoring tools call this without credentials.
    """
    health_status = {
        "status": "healthy",
        "database": "ok",
        "service": "task-scheduler-api",
    }

    # Check database connectivity
    try:
        connection.ensure_connection()
    except OperationalError:
        health_status["status"] = "unhealthy"
        health_status["database"] = "unreachable"
        return Response(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response(health_status, status=status.HTTP_200_OK)