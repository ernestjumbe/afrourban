"""Permission helpers for organization access control."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

if TYPE_CHECKING:
    from organizations.models import Organization


def is_organization_owner(*, user: Any, organization: "Organization") -> bool:
    """Return True when the authenticated user owns the organization."""

    return bool(
        user
        and getattr(user, "is_authenticated", False)
        and organization.owner_id == getattr(user, "pk", None)
    )


class IsOrganizationOwnerOrAdmin(BasePermission):
    """Allow organization writes only to the owner or staff/superuser."""

    message = "You do not have permission to modify this organization."

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Require authentication before object-level checks."""

        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ) -> bool:
        """Allow staff/admins or the organization owner."""

        if request.user.is_staff or request.user.is_superuser:
            return True

        return is_organization_owner(user=request.user, organization=obj)
