"""User selectors for read operations.

Following HackSoftware Django Styleguide: selectors handle read operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db.models import Q, QuerySet

if TYPE_CHECKING:
    from users.models import CustomUser

User = get_user_model()


def user_by_email(*, email: str) -> "CustomUser | None":
    """Get a user by their email address.

    Args:
        email: The user's email address.

    Returns:
        The CustomUser instance or None if not found.
    """
    try:
        return User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return None


def user_with_permissions(*, user_id: int) -> "CustomUser | None":
    """Get a user with their permissions prefetched.

    Optimized query that prefetches groups and permissions
    to avoid N+1 queries when accessing user policies.

    Args:
        user_id: The user's primary key.

    Returns:
        The CustomUser instance with prefetched relations or None.
    """
    try:
        return User.objects.prefetch_related(
            "groups",
            "groups__permissions",
            "user_permissions",
        ).get(pk=user_id)
    except User.DoesNotExist:
        return None


def user_list(
    *,
    is_active: bool | None = None,
    is_staff: bool | None = None,
    search: str | None = None,
    ordering: str = "-date_joined",
) -> QuerySet["CustomUser"]:
    """List users with optional filtering and search.

    Args:
        is_active: Filter by active status (optional).
        is_staff: Filter by staff status (optional).
        search: Search term for email or display name (optional).
        ordering: Sort field with optional '-' prefix for descending.

    Returns:
        QuerySet of CustomUser instances.
    """
    queryset = User.objects.select_related("profile").prefetch_related("groups")

    # Apply filters
    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    if is_staff is not None:
        queryset = queryset.filter(is_staff=is_staff)

    if search:
        queryset = queryset.filter(
            Q(email__icontains=search) | Q(profile__display_name__icontains=search)
        )

    # Validate and apply ordering
    valid_orderings = {
        "date_joined",
        "-date_joined",
        "email",
        "-email",
        "last_login",
        "-last_login",
    }
    if ordering not in valid_orderings:
        ordering = "-date_joined"

    return queryset.order_by(ordering)


def user_get_by_id(*, user_id: int) -> "CustomUser":
    """Get a user by ID with profile and groups prefetched.

    Args:
        user_id: The user's primary key.

    Returns:
        The CustomUser instance.

    Raises:
        User.DoesNotExist: If no user with the given ID exists.
    """
    return (
        User.objects.select_related("profile")
        .prefetch_related(
            "groups",
            "groups__permissions",
            "user_permissions",
        )
        .get(pk=user_id)
    )


def user_permissions_get(*, user: "CustomUser") -> dict[str, Any]:
    """Get user's effective permissions.

    Returns direct permissions, role (group) permissions,
    and the combined effective permission list.

    Args:
        user: The user to get permissions for.

    Returns:
        Dict with direct_permissions, role_permissions, and effective_permissions.
    """
    # Get direct permissions
    direct_perms = user.user_permissions.select_related("content_type").all()
    direct_permissions = [
        {
            "id": p.id,
            "codename": p.codename,
            "name": p.name,
        }
        for p in direct_perms
    ]

    # Get role (group) permissions
    role_permissions = []
    for group in user.groups.prefetch_related("permissions").all():
        group_perms = [
            {
                "id": p.id,
                "codename": p.codename,
                "name": p.name,
            }
            for p in group.permissions.all()
        ]
        role_permissions.append(
            {
                "role": {"id": group.id, "name": group.name},
                "permissions": group_perms,
            }
        )

    # Build effective permissions list (unique codenames)
    effective = set()
    for p in direct_perms:
        effective.add(p.codename)
    for group in user.groups.all():
        for p in group.permissions.all():
            effective.add(p.codename)

    return {
        "user_id": user.pk,
        "direct_permissions": direct_permissions,
        "role_permissions": role_permissions,
        "effective_permissions": sorted(effective),
    }


def permission_list() -> QuerySet[Permission]:
    """List all available permissions.

    Returns:
        QuerySet of Permission instances.
    """
    return Permission.objects.select_related("content_type").all()


# =============================================================================
# Role Selectors (Phase 7: User Story 5)
# =============================================================================


def role_list() -> list[dict[str, Any]]:
    """List all roles with user and permission counts.

    Returns:
        List of dicts with role data including counts.
    """
    from django.contrib.auth.models import Group
    from django.db.models import Count

    roles = Group.objects.annotate(
        user_count=Count("user", distinct=True),
        permission_count=Count("permissions", distinct=True),
    ).order_by("name")

    return [
        {
            "id": role.id,
            "name": role.name,
            "user_count": role.user_count,
            "permission_count": role.permission_count,
        }
        for role in roles
    ]


def role_get_by_id(*, role_id: int) -> dict[str, Any]:
    """Get a role by ID with permissions and policies.

    Args:
        role_id: The role (Group) primary key.

    Returns:
        Dict with role data, permissions, policies, and user count.

    Raises:
        Group.DoesNotExist: If no role with the given ID exists.
    """
    from django.contrib.auth.models import Group
    from django.db.models import Count

    from profiles.models import GroupPolicy

    role = (
        Group.objects.prefetch_related("permissions")
        .annotate(user_count=Count("user", distinct=True))
        .get(pk=role_id)
    )

    # Get permissions
    permissions = [
        {
            "id": p.id,
            "codename": p.codename,
            "name": p.name,
        }
        for p in role.permissions.all()
    ]

    # Get policies via GroupPolicy
    group_policies = GroupPolicy.objects.filter(group=role).select_related("policy")
    policies = [
        {
            "id": gp.policy.id,
            "name": gp.policy.name,
            "is_active": gp.policy.is_active,
        }
        for gp in group_policies
    ]

    return {
        "id": role.id,
        "name": role.name,
        "permissions": permissions,
        "policies": policies,
        "user_count": role.user_count,
    }
