"""
Serializers for the Tasks API.
Handle input validation and output shaping.
"""
from django.utils import timezone
from rest_framework import serializers
from .models import Task, TaskExecution, TaskLog, TaskStatus, TaskPriority


class TaskExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskExecution
        fields = [
            'id', 'outcome', 'error_message',
            'started_at', 'finished_at', 'duration_ms',
            'worker_id', 'created_at',
        ]
        read_only_fields = fields


class TaskLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskLog
        fields = ['id', 'level', 'message', 'created_at']
        read_only_fields = fields


class TaskSerializer(serializers.ModelSerializer):
    """
    Full task serializer — used for GET responses.
    Includes nested execution history and logs.
    """
    executions = TaskExecutionSerializer(many=True, read_only=True)
    logs = TaskLogSerializer(many=True, read_only=True)
    owner_email = serializers.EmailField(source='user.email', read_only=True)
    can_retry = serializers.BooleanField(read_only=True)
    is_terminal = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'scheduled_at', 'executed_at', 'completed_at',
            'retry_count', 'max_retries', 'can_retry', 'is_terminal',
            'celery_task_id', 'owner_email',
            'executions', 'logs',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'retry_count', 'celery_task_id',
            'executed_at', 'completed_at', 'owner_email',
            'can_retry', 'is_terminal', 'created_at', 'updated_at',
        ]


class TaskCreateSerializer(serializers.Serializer):
    """
    Validates input when creating a new task.
    Kept separate from TaskSerializer to keep create/read concerns apart.
    """
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, default='', allow_blank=True)
    scheduled_at = serializers.DateTimeField()
    priority = serializers.ChoiceField(
        choices=TaskPriority.choices,
        default=TaskPriority.NORMAL
    )
    max_retries = serializers.IntegerField(min_value=0, max_value=10, default=3)

    def validate_scheduled_at(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError(
                "Scheduled time must be in the future."
            )
        return value


class TaskUpdateSerializer(serializers.Serializer):
    """
    Validates input when updating a PENDING task.
    All fields are optional — only provided fields are updated.
    """
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    scheduled_at = serializers.DateTimeField(required=False)
    priority = serializers.ChoiceField(choices=TaskPriority.choices, required=False)
    max_retries = serializers.IntegerField(min_value=0, max_value=10, required=False)

    def validate_scheduled_at(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError(
                "Scheduled time must be in the future."
            )
        return value