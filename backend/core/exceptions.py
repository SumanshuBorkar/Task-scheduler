"""
Custom exception handler that normalizes all API error responses
into a consistent JSON shape.

Default DRF errors look like:
  {"detail": "Not found."}
  {"username": ["This field is required."]}

After this handler, all errors look like:
  {
    "success": false,
    "message": "Validation failed.",
    "errors": { "username": ["This field is required."] },
    "status_code": 400
  }
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler.
    Registered in settings.py under REST_FRAMEWORK['EXCEPTION_HANDLER'].
    """
    # First call DRF's default handler to get the standard response
    response = exception_handler(exc, context)

    if response is not None:
        # Normalise the error detail into a consistent structure
        original_data = response.data

        # Extract a human-readable message
        if isinstance(original_data, dict) and 'detail' in original_data:
            message = str(original_data['detail'])
            errors = {}
        elif isinstance(original_data, dict):
            message = "Validation failed."
            errors = original_data
        elif isinstance(original_data, list):
            message = "Request failed."
            errors = {"non_field_errors": original_data}
        else:
            message = "An error occurred."
            errors = {}

        response.data = {
            "success": False,
            "message": message,
            "errors": errors,
            "status_code": response.status_code,
        }

    return response


class ServiceError(Exception):
    """
    Raised by service layer functions when a business rule is violated.
    Views catch this and convert it to a 400 response.

    Usage in a service:
        raise ServiceError("Cannot schedule a task in the past.")

    Usage in a view:
        try:
            task_services.create_task(...)
        except ServiceError as e:
            return Response({"message": str(e)}, status=400)
    """
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(ServiceError):
    """Raised when a requested resource does not exist."""
    def __init__(self, message: str = "Resource not found."):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class PermissionError(ServiceError):
    """Raised when a user tries to access a resource they don't own."""
    def __init__(self, message: str = "You do not have permission to perform this action."):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)