"""
Task API ViewSet.
Views are intentionally thin — they validate input, call services/selectors,
and return responses. No business logic lives here.
"""
import logging
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.exceptions import ServiceError, NotFoundError
from core.pagination import StandardPagination
from .selectors import get_tasks_for_user, get_task_for_user
from .serializers import (
    TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer
)
from . import services

logger = logging.getLogger(__name__)


class TaskViewSet(ViewSet):
    """
    ViewSet providing full CRUD + custom actions for Tasks.

    Routes (after registering with router in urls.py):
      GET    /api/tasks/              → list()
      POST   /api/tasks/              → create()
      GET    /api/tasks/{id}/         → retrieve()
      PATCH  /api/tasks/{id}/         → partial_update()
      DELETE /api/tasks/{id}/         → destroy()
      POST   /api/tasks/{id}/complete/ → complete()
      POST   /api/tasks/{id}/cancel/   → cancel()
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """GET /api/tasks/ — list all tasks for the current user."""
        filters = {
            'status': request.query_params.get('status'),
            'priority': request.query_params.get('priority'),
            'search': request.query_params.get('search'),
        }
        tasks = get_tasks_for_user(user=request.user, filters=filters)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(tasks, request)
        serializer = TaskSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        """POST /api/tasks/ — create a new scheduled task."""
        serializer = TaskCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            task = services.create_task(
                user=request.user,
                **serializer.validated_data
            )
        except ServiceError as e:
            return Response(
                {"success": False, "message": e.message},
                status=e.status_code
            )

        return Response(
            {"success": True, "task": TaskSerializer(task).data},
            status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, pk=None):
        """GET /api/tasks/{id}/ — get a single task."""
        task = get_task_for_user(task_id=pk, user=request.user)
        if not task:
            return Response(
                {"success": False, "message": "Task not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {"success": True, "task": TaskSerializer(task).data}
        )

    def partial_update(self, request, pk=None):
        """PATCH /api/tasks/{id}/ — update a PENDING task."""
        serializer = TaskUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            task = services.update_task(
                task_id=pk,
                user=request.user,
                **serializer.validated_data
            )
        except (ServiceError, NotFoundError) as e:
            return Response(
                {"success": False, "message": e.message},
                status=e.status_code
            )

        return Response(
            {"success": True, "task": TaskSerializer(task).data}
        )

    def destroy(self, request, pk=None):
        """DELETE /api/tasks/{id}/ — delete a task."""
        task = get_task_for_user(task_id=pk, user=request.user)
        if not task:
            return Response(
                {"success": False, "message": "Task not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if task.status == 'RUNNING':
            return Response(
                {"success": False, "message": "Cannot delete a running task."},
                status=status.HTTP_400_BAD_REQUEST
            )

        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        """POST /api/tasks/{id}/complete/ — manually mark a task as completed."""
        try:
            task = services.complete_task(task_id=pk, user=request.user)
        except (ServiceError, NotFoundError) as e:
            return Response(
                {"success": False, "message": e.message},
                status=e.status_code
            )
        return Response(
            {"success": True, "task": TaskSerializer(task).data}
        )

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """POST /api/tasks/{id}/cancel/ — cancel a pending/scheduled task."""
        try:
            task = services.cancel_task(task_id=pk, user=request.user)
        except (ServiceError, NotFoundError) as e:
            return Response(
                {"success": False, "message": e.message},
                status=e.status_code
            )
        return Response(
            {"success": True, "task": TaskSerializer(task).data}
        )