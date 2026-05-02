"""Permission helpers for event access control."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from organizations.permissions import is_organization_owner

if TYPE_CHECKING:
    from events.models import Event


def is_personal_event_owner(*, user: Any, event: "Event") -> bool:
    """Return True when the authenticated user owns the personal event."""

    return bool(
        user
        and getattr(user, "is_authenticated", False)
        and event.owner_id == getattr(user, "pk", None)
    )


def can_write_event(*, user: Any, event: "Event") -> bool:
    """Return True when the actor may mutate the event."""

    if not user or not getattr(user, "is_authenticated", False):
        return False

    if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
        return True

    if event.owner_id is not None:
        return is_personal_event_owner(user=user, event=event)

    if event.organization_id is not None:
        return is_organization_owner(user=user, organization=event.organization)

    return False


class IsEventWriteActorOrAdmin(BasePermission):
    """Allow event writes only to the effective owner or admins."""

    message = "You do not have permission to modify this event."

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Require authentication before object-level checks."""

        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ) -> bool:
        """Allow staff/admins or the effective event owner."""

        return can_write_event(user=request.user, event=obj)
