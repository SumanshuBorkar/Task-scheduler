"""
Register task models with Django admin.
This lets you inspect tasks, executions, and logs at /admin/
"""
from django.contrib import admin
from .models import Task, TaskExecution, TaskLog


class TaskExecutionInline(admin.TabularInline):
    """Shows execution history inline on the Task detail page."""
    model = TaskExecution
    extra = 0
    readonly_fields = [
        'id', 'started_at', 'finished_at',
        'outcome', 'error_message', 'duration_ms', 'worker_id'
    ]
    can_delete = False


class TaskLogInline(admin.TabularInline):
    """Shows log entries inline on the Task detail page."""
    model = TaskLog
    extra = 0
    readonly_fields = ['id', 'level', 'message', 'created_at']
    can_delete = False


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'status', 'priority',
        'scheduled_at', 'retry_count', 'created_at'
    ]
    list_filter = ['status', 'priority']
    search_fields = ['title', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'celery_task_id']
    ordering = ['-created_at']
    inlines = [TaskExecutionInline, TaskLogInline]


@admin.register(TaskExecution)
class TaskExecutionAdmin(admin.ModelAdmin):
    list_display = ['task', 'outcome', 'started_at', 'finished_at', 'duration_ms']
    list_filter = ['outcome']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(TaskLog)
class TaskLogAdmin(admin.ModelAdmin):
    list_display = ['task', 'level', 'message', 'created_at']
    list_filter = ['level']
    readonly_fields = ['id', 'created_at']