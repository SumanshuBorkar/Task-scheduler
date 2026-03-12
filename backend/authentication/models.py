"""
Custom User model.
Must be defined before the first migration is ever run.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model extending Django's built-in AbstractUser.

    We override groups and user_permissions with unique related_names
    to avoid reverse accessor clashes with auth.User.
    """
    email = models.EmailField(
        unique=True,
        help_text="Required. Used for login and notifications."
    )

    # Fix: override both ManyToMany fields with unique related_names
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='authentication_users',   # ← unique name, no clash
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='authentication_users',   # ← unique name, no clash
        help_text='Specific permissions for this user.',
    )

    # Make email the login identifier instead of username
    USERNAME_FIELD = 'email'

    # username is still required when creating via CLI (createsuperuser)
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.email