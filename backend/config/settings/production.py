"""
Production settings.
Inherits from base and enforces security hardening.
"""
from .base import *

DEBUG = False

# In production, only serve from known hosts
ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS').split(',')

# Enforce HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True