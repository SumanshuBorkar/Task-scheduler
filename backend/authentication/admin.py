from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Registers our custom User model with the Django admin panel.
    Inherits all of Django's built-in user admin functionality.
    """
    list_display = ['email', 'username', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'is_staff']
    search_fields = ['email', 'username']
    ordering = ['-date_joined']

    # Add email to the fieldsets shown in the admin edit form
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ()}),
    )