"""DRF permission classes for access control.

Custom permission classes that check JWT token claims
and user attributes for authorization decisions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

if TYPE_CHECKING:
    pass


class HasPermission(BasePermission):
    """Check if user has a specific permission via token claims.

    Usage:
        class MyView(APIView):
            permission_classes = [HasPermission]
            required_permission = "posts.add_post"

    The permission is checked against the 'permissions' claim in the JWT
    and also against Django's standard permission system as fallback.
    """

    message = "You do not have permission to perform this action."

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check permission against token claims and Django permissions.

        Args:
            request: The incoming request.
            view: The view being accessed.

        Returns:
            True if user has the required permission.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        required_permission = getattr(view, "required_permission", None)
        if not required_permission:
            return True

        # Check token claims first (if available via JWT)
        token_permissions = self._get_token_permissions(request)
        if required_permission in token_permissions:
            return True

        # Fallback to Django's permission system
        return request.user.has_perm(required_permission)

    def _get_token_permissions(self, request: Request) -> list[str]:
        """Extract permissions from JWT token claims.

        Args:
            request: The incoming request.

        Returns:
            List of permission strings from the token.
        """
        # JWT claims are stored in request.auth for simplejwt
        if hasattr(request, "auth") and request.auth:
            return request.auth.get("permissions", [])
        return []


class IsStaffUser(BasePermission):
    """Restrict access to staff users only.

    Usage:
        class AdminView(APIView):
            permission_classes = [IsStaffUser]
    """

    message = "You must be a staff member to access this resource."

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check if user is staff.

        Args:
            request: The incoming request.
            view: The view being accessed.

        Returns:
            True if user is authenticated and is_staff=True.
        """
        return bool(
            request.user and request.user.is_authenticated and request.user.is_staff
        )


class IsOwnerOrAdmin(BasePermission):
    """Allow access to object owner or admin/staff users.

    For object-level permission checking. The object must have
    a 'user' attribute or the view must define 'owner_field'.

    Usage:
        class ProfileView(APIView):
            permission_classes = [IsOwnerOrAdmin]
            owner_field = "user"  # optional, defaults to "user"
    """

    message = "You do not have permission to access this resource."

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check if user is authenticated.

        Args:
            request: The incoming request.
            view: The view being accessed.

        Returns:
            True if user is authenticated.
        """
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """Check if user is owner or admin.

        Args:
            request: The incoming request.
            view: The view being accessed.
            obj: The object being accessed.

        Returns:
            True if user is the owner or is staff/superuser.
        """
        # Admins can access anything
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Get owner field name from view or use default
        owner_field = getattr(view, "owner_field", "user")

        # Get the owner from the object
        owner = getattr(obj, owner_field, None)

        # Handle OneToOne reverse relations (e.g., profile.user)
        if owner is None:
            return False

        # Compare user IDs
        owner_id = owner.pk if hasattr(owner, "pk") else owner
        return request.user.pk == owner_id


class IsSuperUser(BasePermission):
    """Restrict access to superusers only.

    Usage:
        class SuperAdminView(APIView):
            permission_classes = [IsSuperUser]
    """

    message = "You must be a superuser to access this resource."

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check if user is superuser.

        Args:
            request: The incoming request.
            view: The view being accessed.

        Returns:
            True if user is authenticated and is_superuser=True.
        """
        return bool(
            request.user and request.user.is_authenticated and request.user.is_superuser
        )
