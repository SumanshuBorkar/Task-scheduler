"""
Development settings.
Inherits everything from base and adds dev-only configuration.
"""
from .base import *

DEBUG = True

# In development, allow all hosts for convenience
ALLOWED_HOSTS = ['*']

# Show full error details in API responses during development
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',  # Enables the DRF browser UI
)