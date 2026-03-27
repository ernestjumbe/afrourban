"""User services for business logic operations.

Following HackSoftware Django Styleguide: services handle write operations.
"""

from __future__ import annotations

import secrets
from datetime import timedelta
from typing import TYPE_CHECKING

import structlog
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from profiles.models import Profile
from users.conf import app_settings

if TYPE_CHECKING:
    from django.contrib.auth.models import Group

    from users.models import CustomUser, EmailVerificationToken

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
    CustomUser and Profile in a single transaction. If an unverified
    account already exists for the given email, it is superseded
    (deleted and replaced).

    Args:
        email: User's email address (used as login identifier).
        password: User's password (will be hashed).
        display_name: Optional public display name for the profile.

    Returns:
        The created CustomUser instance with profile attached.

    Raises:
        IntegrityError: If a *verified* email already exists.
    """
    # Supersede any existing unverified account (CASCADE deletes token)
    existing_unverified = User.objects.filter(
        email__iexact=email, is_email_verified=False
    )
    if existing_unverified.exists():
        logger.info("email_verification_superseded", email=email)
        existing_unverified.delete()

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

    # Create verification token and send email
    token_obj = email_verification_token_create(user=user)
    email_verification_send(user=user, token_obj=token_obj)

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
# Email Verification Services
# =============================================================================


def email_verification_token_create(
    *,
    user: "CustomUser",
) -> "EmailVerificationToken":
    """Create an email verification token for a user.

    Generates a cryptographically secure token and persists it.

    Args:
        user: The user to create a token for.

    Returns:
        The created EmailVerificationToken instance.
    """
    from users.models import EmailVerificationToken

    token_value = secrets.token_urlsafe(32)
    expires_at = timezone.now() + timedelta(
        days=app_settings.EMAIL_VERIFICATION_TOKEN_EXPIRY_DAYS,
    )

    return EmailVerificationToken.objects.create(
        user=user,
        token=token_value,
        expires_at=expires_at,
    )


def email_verification_send(
    *,
    user: "CustomUser",
    token_obj: "EmailVerificationToken",
) -> None:
    """Send a verification email to the user.

    Renders both HTML and plain-text templates and dispatches
    via Django's ``send_mail``.

    Args:
        user: The recipient user.
        token_obj: The verification token to embed in the link.
    """
    verification_url = (
        f"{app_settings.EMAIL_VERIFICATION_BASE_URL}"
        f"/registration/email-verification?token={token_obj.token}"
    )
    site_name = app_settings.EMAIL_VERIFICATION_SITE_NAME
    expiry_days = app_settings.EMAIL_VERIFICATION_TOKEN_EXPIRY_DAYS

    context = {
        "user": user,
        "verification_url": verification_url,
        "base_url": app_settings.EMAIL_VERIFICATION_BASE_URL,
        "expiry_days": expiry_days,
        "site_name": site_name,
    }

    text_body = render_to_string("users/emails/email_verification.txt", context)
    html_body = render_to_string("users/emails/email_verification.html", context)

    send_mail(
        subject=f"Verify your email address \u2013 {site_name}",
        message=text_body,
        from_email=app_settings.EMAIL_VERIFICATION_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_body,
    )


def email_verification_verify(*, token: str) -> None:
    """Verify an email address using the supplied token.

    On success the user's email is marked verified and the token
    is deleted. Expired tokens are also deleted.

    Args:
        token: The opaque token string.

    Raises:
        ValidationError: With ``code="token_invalid"`` if the token
            does not exist, or ``code="token_expired"`` if expired.
    """
    from users.selectors import email_verification_token_get_by_token

    token_obj = email_verification_token_get_by_token(token=token)

    if token_obj is None:
        raise ValidationError(
            detail="Verification token is invalid.",
            code="token_invalid",
        )

    if timezone.now() >= token_obj.expires_at:
        token_obj.delete()
        logger.info(
            "email_verification_token_expired",
            user_id=token_obj.user.id,
        )
        raise ValidationError(
            detail="Verification token has expired.",
            code="token_expired",
        )

    with transaction.atomic():
        token_obj.user.is_email_verified = True
        token_obj.user.save(update_fields=["is_email_verified"])
        token_obj.delete()

    logger.info("email_verified", user_id=token_obj.user.id)


def email_verification_resend(*, email: str) -> None:
    """Resend a verification email for the given address.

    Enumeration-safe: always returns without raising, regardless
    of whether the email exists or is already verified.

    Args:
        email: The email address to resend verification for.
    """
    from users.models import EmailVerificationToken

    user = User.objects.filter(email__iexact=email).first()

    if user is None or user.is_email_verified:
        return

    EmailVerificationToken.objects.filter(user=user).delete()

    token_obj = email_verification_token_create(user=user)
    email_verification_send(user=user, token_obj=token_obj)

    logger.info("email_verification_resend_sent", user_id=user.id, email=email)


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
