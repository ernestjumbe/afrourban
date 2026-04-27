"""Selectors for organization read operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Q, QuerySet

from organizations.models import Organization

if TYPE_CHECKING:
    from users.models import CustomUser

VALID_ORGANIZATION_ORDERINGS = {
    "name",
    "-name",
    "created_at",
    "-created_at",
}


def organization_get_by_id(*, organization_id: int) -> Organization:
    """Return one organization with its owner loaded."""

    return Organization.objects.select_related("owner").get(pk=organization_id)


def organization_list(
    *,
    owner: "CustomUser | None" = None,
    owner_scope: str = "all",
    organization_type: str | None = None,
    is_online_only: bool | None = None,
    search: str | None = None,
    ordering: str = "-created_at",
) -> QuerySet[Organization]:
    """List organizations with the planned filter and ordering options."""

    queryset = Organization.objects.select_related("owner")
    normalized_owner_scope = owner_scope.strip().lower() if owner_scope else "all"

    if normalized_owner_scope == "mine" and owner is not None:
        queryset = queryset.filter(owner=owner)

    if organization_type:
        queryset = queryset.filter(organization_type=organization_type)

    if is_online_only is not None:
        queryset = queryset.filter(is_online_only=is_online_only)

    if search:
        search = search.strip()

    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

    if ordering not in VALID_ORGANIZATION_ORDERINGS:
        ordering = "-created_at"

    return queryset.order_by(ordering, "pk")
