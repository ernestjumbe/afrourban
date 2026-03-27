"""JWT claims builder for embedding user policies in tokens.

This module provides functions to build custom claims that are
embedded in JWT tokens, including user roles, permissions, and policies.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib.auth.models import Permission

if TYPE_CHECKING:
    from users.models import CustomUser


def get_user_policies(user: "CustomUser") -> dict[str, Any]:
    """Get user's roles, permissions, and policies for JWT claims.

    Retrieves the user's group memberships (roles), their
    associated permissions, and active policies to embed in the JWT token.

    Args:
        user: The CustomUser instance.

    Returns:
        Dictionary containing roles, permissions, and active_policies lists.
    """
    from profiles.models import GroupPolicy

    # Get role names from user's groups
    roles = list(user.groups.values_list("name", flat=True))

    # Get all permissions: direct + from groups
    if user.is_superuser:
        # Superusers have all permissions
        permissions = list(Permission.objects.values_list("codename", flat=True))
    else:
        # Get permissions from groups and direct assignments
        group_permissions = Permission.objects.filter(group__user=user).values_list(
            "codename", flat=True
        )

        direct_permissions = user.user_permissions.values_list("codename", flat=True)

        permissions = list(set(group_permissions) | set(direct_permissions))

    # Get active policies from user's groups
    group_ids = user.groups.values_list("id", flat=True)
    active_policies = list(
        GroupPolicy.objects.filter(
            group_id__in=group_ids,
            policy__is_active=True,
        )
        .values_list("policy__name", flat=True)
        .distinct()
    )

    return {
        "roles": roles,
        "permissions": permissions,
        "active_policies": active_policies,
    }


def build_token_claims(user: "CustomUser") -> dict[str, Any]:
    """Build custom claims to embed in JWT token.

    Creates the claims dictionary that will be added to the
    JWT token payload as private claims.

    Args:
        user: The CustomUser instance.

    Returns:
        Dictionary of claims to embed in the token.
    """
    policies = get_user_policies(user)

    return {
        "user_id": user.pk,
        "email": user.email,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "policies": policies,
    }
