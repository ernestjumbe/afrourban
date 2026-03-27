"""User services for business logic operations.

Following HackSoftware Django Styleguide: services handle write operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db import transaction

from profiles.models import Profile

if TYPE_CHECKING:
    from users.models import CustomUser

User = get_user_model()
logger = structlog.get_logger(__name__)


@transaction.atomic
def user_create(
    *,
    email: str,
    password: str,
    display_name: str = "",
) -> "CustomUser":
    """Create a new user with an associated profile.

    This is the primary registration service. Creates both the
    CustomUser and Profile in a single transaction.

    Args:
        email: User's email address (used as login identifier).
        password: User's password (will be hashed).
        display_name: Optional public display name for the profile.

    Returns:
        The created CustomUser instance with profile attached.

    Raises:
        IntegrityError: If email already exists.
    """
    user = User.objects.create_user(
        email=email,
        password=password,
    )

    Profile.objects.create(
        user=user,
        display_name=display_name,
    )

    logger.info(
        "user_created",
        user_id=user.id,
        email=user.email,
    )

    return user


@transaction.atomic
def user_activate(*, user: "CustomUser") -> "CustomUser":
    """Activate a user account.

    Args:
        user: The user to activate.

    Returns:
        The activated user instance.
    """
    user.is_active = True
    user.save(update_fields=["is_active"])
    return user


@transaction.atomic
def user_deactivate(*, user: "CustomUser") -> "CustomUser":
    """Deactivate a user account.

    Args:
        user: The user to deactivate.

    Returns:
        The deactivated user instance.
    """
    user.is_active = False
    user.save(update_fields=["is_active"])
    return user


@transaction.atomic
def user_permissions_set(
    *, user: "CustomUser", permission_ids: list[int]
) -> list[Permission]:
    """Set user's direct permissions (replaces existing).

    Args:
        user: The user to update permissions for.
        permission_ids: List of permission IDs to assign.

    Returns:
        List of assigned Permission instances.
    """
    permissions = Permission.objects.filter(pk__in=permission_ids)
    user.user_permissions.set(permissions)
    return list(permissions)


@transaction.atomic
def user_update(
    *,
    user: "CustomUser",
    is_staff: bool | None = None,
    group_ids: list[int] | None = None,
) -> "CustomUser":
    """Update user account settings.

    Args:
        user: The user to update.
        is_staff: New staff status (optional).
        group_ids: List of group (role) IDs to assign (optional).

    Returns:
        The updated user instance.
    """
    from django.contrib.auth.models import Group

    fields_to_update = []

    if is_staff is not None:
        user.is_staff = is_staff
        fields_to_update.append("is_staff")

    if fields_to_update:
        user.save(update_fields=fields_to_update)

    if group_ids is not None:
        groups = Group.objects.filter(pk__in=group_ids)
        user.groups.set(groups)

    return user


# =============================================================================
# Role Services (Phase 7: User Story 5)
# =============================================================================


@transaction.atomic
def role_create(
    *,
    name: str,
    permission_ids: list[int] | None = None,
) -> "Group":
    """Create a new role (Django Group) with optional permissions.

    Args:
        name: Unique role name.
        permission_ids: List of permission IDs to assign (optional).

    Returns:
        The created Group instance.

    Raises:
        IntegrityError: If role name already exists.
    """
    from django.contrib.auth.models import Group

    group = Group.objects.create(name=name)

    if permission_ids:
        permissions = Permission.objects.filter(pk__in=permission_ids)
        group.permissions.set(permissions)

    return group


@transaction.atomic
def role_update(
    *,
    role: "Group",
    name: str | None = None,
    permission_ids: list[int] | None = None,
) -> "Group":
    """Update a role's name and/or permissions.

    Args:
        role: The Group instance to update.
        name: New role name (optional).
        permission_ids: List of permission IDs to assign, replaces existing (optional).

    Returns:
        The updated Group instance.
    """
    from django.contrib.auth.models import Group

    if name is not None:
        role.name = name
        role.save(update_fields=["name"])

    if permission_ids is not None:
        permissions = Permission.objects.filter(pk__in=permission_ids)
        role.permissions.set(permissions)

    return role


@transaction.atomic
def role_delete(*, role: "Group", force: bool = False) -> None:
    """Delete a role.

    Args:
        role: The Group instance to delete.
        force: If True, delete even if users are assigned.

    Raises:
        ValueError: If role has assigned users and force is False.
    """
    if not force and role.user_set.exists():
        raise ValueError(
            "Cannot delete role with assigned users. "
            "Remove users first or use force=True."
        )

    role.delete()


# =============================================================================
# Password Management Services (Phase 8: User Story 6)
# =============================================================================


from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


def password_reset_request(*, email: str) -> dict[str, str] | None:
    """Request a password reset for a user.

    Generates a password reset token if user exists.
    Returns None if user doesn't exist (to prevent email enumeration).

    Args:
        email: Email address for the account.

    Returns:
        Dict with uid and token if user exists, None otherwise.
        In production, this would queue an email instead of returning the token.
    """
    try:
        user = User.objects.get(email__iexact=email, is_active=True)
    except User.DoesNotExist:
        # Return None silently to prevent email enumeration
        logger.info("password_reset_requested", email=email, user_found=False)
        return None

    # Generate token
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    logger.info(
        "password_reset_requested",
        user_id=user.id,
        email=user.email,
        user_found=True,
    )

    # In production, queue email here instead of returning token
    # For now, return the data for testing purposes
    return {
        "uid": uid,
        "token": token,
        "email": user.email,
    }


@transaction.atomic
def password_reset_confirm(*, token: str, password: str) -> "CustomUser":
    """Confirm a password reset with token and set new password.

    The token format is: base64(uid):token

    Args:
        token: Combined token string from email (uid:token format)
        password: New password to set.

    Returns:
        The user with updated password.

    Raises:
        ValueError: If token is invalid or expired.
    """
    # Parse the combined token (format: uid:token)
    try:
        if ":" in token:
            uid_b64, reset_token = token.split(":", 1)
        else:
            raise ValueError("Invalid token format")

        uid = force_str(urlsafe_base64_decode(uid_b64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        logger.warning("password_reset_confirm_failed", reason="invalid_token")
        raise ValueError("The password reset token is invalid or has expired.") from e

    # Verify token
    if not default_token_generator.check_token(user, reset_token):
        logger.warning(
            "password_reset_confirm_failed",
            user_id=user.id,
            reason="expired_token",
        )
        raise ValueError("The password reset token is invalid or has expired.")

    # Set new password
    user.set_password(password)
    user.save(update_fields=["password"])

    logger.info(
        "password_reset_confirmed",
        user_id=user.id,
        email=user.email,
    )

    return user


@transaction.atomic
def password_change(
    *, user: "CustomUser", old_password: str, new_password: str
) -> "CustomUser":
    """Change password for authenticated user.

    Args:
        user: The authenticated user.
        old_password: Current password for verification.
        new_password: New password to set.

    Returns:
        The user with updated password.

    Raises:
        ValueError: If old password is incorrect.
    """
    if not user.check_password(old_password):
        logger.warning(
            "password_change_failed",
            user_id=user.id,
            reason="incorrect_password",
        )
        raise ValueError("Current password is incorrect.")

    user.set_password(new_password)
    user.save(update_fields=["password"])

    logger.info(
        "password_changed",
        user_id=user.id,
        email=user.email,
    )

    return user
