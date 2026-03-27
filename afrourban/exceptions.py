"""RFC 9457 Problem Details exception handler for Django REST Framework.

This module provides a standardized error response format following RFC 9457
(Problem Details for HTTP APIs).
"""

from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def problem_details_exception_handler(
    exc: Exception, context: dict[str, Any]
) -> Response | None:
    """Convert exceptions to RFC 9457 Problem Details format.

    Args:
        exc: The exception that was raised.
        context: Dictionary containing additional context (view, args, kwargs, request).

    Returns:
        Response with Problem Details format or None if DRF can't handle the exception.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is None:
        return None

    # Get request info for the instance URI
    request = context.get("request")
    instance = request.path if request else None

    # Build RFC 9457 Problem Details response
    problem_detail: dict[str, Any] = {
        "type": "about:blank",
        "title": _get_error_title(response.status_code),
        "status": response.status_code,
        "instance": instance,
    }

    # Extract detail from various error formats
    if isinstance(response.data, dict):
        if "detail" in response.data:
            problem_detail["detail"] = response.data["detail"]
        else:
            # Field validation errors
            problem_detail["detail"] = "Validation failed"
            problem_detail["errors"] = response.data
    elif isinstance(response.data, list):
        problem_detail["detail"] = (
            response.data[0] if response.data else "An error occurred"
        )
        if len(response.data) > 1:
            problem_detail["errors"] = response.data
    else:
        problem_detail["detail"] = str(response.data)

    response.data = problem_detail
    response.content_type = "application/problem+json"

    return response


def _get_error_title(status_code: int) -> str:
    """Get a human-readable title for an HTTP status code.

    Args:
        status_code: The HTTP status code.

    Returns:
        A string title for the status code.
    """
    titles = {
        status.HTTP_400_BAD_REQUEST: "Bad Request",
        status.HTTP_401_UNAUTHORIZED: "Unauthorized",
        status.HTTP_403_FORBIDDEN: "Forbidden",
        status.HTTP_404_NOT_FOUND: "Not Found",
        status.HTTP_405_METHOD_NOT_ALLOWED: "Method Not Allowed",
        status.HTTP_406_NOT_ACCEPTABLE: "Not Acceptable",
        status.HTTP_409_CONFLICT: "Conflict",
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: "Unsupported Media Type",
        status.HTTP_422_UNPROCESSABLE_ENTITY: "Unprocessable Entity",
        status.HTTP_429_TOO_MANY_REQUESTS: "Too Many Requests",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
        status.HTTP_502_BAD_GATEWAY: "Bad Gateway",
        status.HTTP_503_SERVICE_UNAVAILABLE: "Service Unavailable",
    }
    return titles.get(status_code, "Error")
