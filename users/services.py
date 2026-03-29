"""User services for business logic operations.

Following HackSoftware Django Styleguide: services handle write operations.
"""

from __future__ import annotations

import json
import re
import secrets
import uuid
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import structlog
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from profiles.models import Profile
from users.conf import app_settings

if TYPE_CHECKING:
    from django.contrib.auth.models import Group

    from users.models import CustomUser, EmailVerificationToken, WebAuthnCredential

User = get_user_model()
logger = structlog.get_logger(__name__)

USERNAME_INPUT_MIN_LENGTH = int(getattr(User, "USERNAME_INPUT_MIN_LENGTH", 3))
USERNAME_INPUT_MAX_LENGTH = int(getattr(User, "USERNAME_INPUT_MAX_LENGTH", 30))
USERNAME_INPUT_PATTERN = str(
    getattr(
        User,
        "USERNAME_INPUT_PATTERN",
        r"^(?=.{3,30}$)(?!\.)(?=.*[A-Za-z])[A-Za-z0-9_.]+$",
    )
)
USERNAME_INPUT_RE = re.compile(USERNAME_INPUT_PATTERN)


def normalize_username(*, username: str) -> str:
    """Normalize username input before validation and persistence."""

    return username.strip()


def username_has_valid_format(*, username: str) -> bool:
    """Check if username matches the agreed format policy."""

    normalized_username = normalize_username(username=username)
    return bool(USERNAME_INPUT_RE.fullmatch(normalized_username))


def validate_username_format(*, username: str) -> str:
    """Validate username format and return normalized value.

    Raises:
        ValidationError: If username does not match the supported format.
    """

    normalized_username = normalize_username(username=username)
    is_valid = username_has_valid_format(username=normalized_username)

    log_username_outcome(
        outcome="valid_format" if is_valid else "invalid_format",
        username=normalized_username,
    )

    if not is_valid:
        raise ValidationError(
            {
                "username": [
                    "Username must be 3-30 characters, contain at least one letter, "
                    "not start with '.', and use only letters, numbers, '_' or '.'."
                ]
            }
        )

    return normalized_username


def username_is_taken(*, username: str, exclude_user_id: int | None = None) -> bool:
    """Check if username is already taken (case-insensitive)."""

    normalized_username = normalize_username(username=username)
    queryset = User.objects.filter(username__iexact=normalized_username)
    if exclude_user_id is not None:
        queryset = queryset.exclude(pk=exclude_user_id)

    is_taken = queryset.exists()
    log_username_outcome(
        outcome="username_taken" if is_taken else "username_available",
        username=normalized_username,
        user_id=exclude_user_id,
    )
    return is_taken


def log_username_outcome(
    *,
    outcome: str,
    username: str | None,
    user_id: int | None = None,
    reason: str | None = None,
) -> None:
    """Log structured username operation outcomes for observability."""

    logger.info(
        "username_operation_outcome",
        outcome=outcome,
        username=username,
        user_id=user_id,
        reason=reason,
    )


def log_username_cooldown_outcome(
    *,
    outcome: str,
    user_id: int | None,
    cooldown_days: int | None = None,
    username_changed_at: datetime | None = None,
    next_allowed_at: datetime | None = None,
) -> None:
    """Log structured cooldown evaluation outcomes."""

    logger.info(
        "username_cooldown_outcome",
        outcome=outcome,
        user_id=user_id,
        cooldown_days=cooldown_days,
        username_changed_at=username_changed_at,
        next_allowed_at=next_allowed_at,
    )


def log_email_visibility_outcome(
    *,
    outcome: str,
    viewer_user_id: int | None,
    subject_user_id: int | None,
    viewer_is_staff: bool,
    is_owned: bool,
    email_visible: bool,
    source: str = "users",
) -> None:
    """Log structured email-visibility projection outcomes."""

    logger.info(
        "email_visibility_outcome",
        outcome=outcome,
        viewer_user_id=viewer_user_id,
        subject_user_id=subject_user_id,
        viewer_is_staff=viewer_is_staff,
        is_owned=is_owned,
        email_visible=email_visible,
        source=source,
    )


@transaction.atomic
def username_change(*, user: "CustomUser", username: str) -> dict[str, object]:
    """Change a user's username when cooldown and uniqueness rules allow it."""

    normalized_username = validate_username_format(username=username)
    cooldown_days = app_settings.USERNAME_CHANGE_COOLDOWN_DAYS
    now = timezone.now()
    current_username_changed_at = user.username_changed_at

    if current_username_changed_at is not None:
        next_allowed_at = current_username_changed_at + timedelta(days=cooldown_days)
        if now < next_allowed_at:
            log_username_outcome(
                outcome="cooldown_active",
                username=normalized_username,
                user_id=user.pk,
                reason="cooldown_active",
            )
            log_username_cooldown_outcome(
                outcome="cooldown_active",
                user_id=user.pk,
                cooldown_days=cooldown_days,
                username_changed_at=current_username_changed_at,
                next_allowed_at=next_allowed_at,
            )
            raise ValidationError(
                detail=(
                    "Username can be changed again at "
                    f"{next_allowed_at.isoformat()}."
                ),
                code="cooldown_active",
            )

    if username_is_taken(username=normalized_username, exclude_user_id=user.pk):
        raise ValidationError({"username": ["This username is already in use."]})

    user.username = normalized_username
    user.username_changed_at = now

    try:
        user.save(update_fields=["username", "username_changed_at"])
    except IntegrityError as exc:
        log_username_outcome(
            outcome="username_taken",
            username=normalized_username,
            user_id=user.pk,
            reason="integrity_error",
        )
        raise ValidationError({"username": ["This username is already in use."]}) from exc

    next_allowed_at = now + timedelta(days=cooldown_days)

    log_username_outcome(
        outcome="success",
        username=user.username,
        user_id=user.pk,
    )
    log_username_cooldown_outcome(
        outcome="cooldown_started",
        user_id=user.pk,
        cooldown_days=cooldown_days,
        username_changed_at=user.username_changed_at,
        next_allowed_at=next_allowed_at,
    )

    return {
        "id": user.pk,
        "username": user.username,
        "cooldown_days": cooldown_days,
        "next_allowed_at": next_allowed_at,
    }


@transaction.atomic
def user_create(
    *,
    email: str,
    password: str,
    username: str,
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
        username: Account username supplied during registration.
        display_name: Optional public display name for the profile.

    Returns:
        The created CustomUser instance with profile attached.

    Raises:
        IntegrityError: If a *verified* email already exists.
    """
    normalized_username = validate_username_format(username=username)

    # Supersede any existing unverified account (CASCADE deletes token)
    existing_unverified = User.objects.filter(
        email__iexact=email, is_email_verified=False
    )

    existing_unverified_user = existing_unverified.only("id").first()
    exclude_user_id = (
        existing_unverified_user.pk if existing_unverified_user is not None else None
    )
    if username_is_taken(
        username=normalized_username,
        exclude_user_id=exclude_user_id,
    ):
        raise ValidationError({"username": ["This username is already in use."]})

    if existing_unverified.exists():
        logger.info("email_verification_superseded", email=email)
        existing_unverified.delete()

    user = User.objects.create_user(
        email=email,
        password=password,
        username=normalized_username,
    )

    Profile.objects.create(
        user=user,
        display_name=display_name,
    )

    logger.info(
        "user_created",
        user_id=user.id,
        email=user.email,
        username=user.username,
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


# =============================================================================
# WebAuthn / Passkey Services
# =============================================================================

CHALLENGE_CACHE_PREFIX = "webauthn_challenge"


def _challenge_cache_key(challenge_id: str) -> str:
    return f"{CHALLENGE_CACHE_PREFIX}:{challenge_id}"


def store_challenge(
    *,
    challenge: bytes,
    ceremony: str,
    email: str | None = None,
    display_name: str = "",
    webauthn_user_id: bytes | None = None,
) -> str:
    """Store a WebAuthn challenge in the cache.

    Args:
        challenge: The raw challenge bytes.
        ceremony: Either "registration" or "authentication".
        email: Email associated with this challenge (registration only).
        display_name: Display name for registration.
        webauthn_user_id: The random user handle bytes (registration only).

    Returns:
        A UUID challenge_id used to retrieve the challenge later.
    """
    import base64

    challenge_id = str(uuid.uuid4())
    payload = {
        "challenge": base64.b64encode(challenge).decode("ascii"),
        "ceremony": ceremony,
    }
    if email is not None:
        payload["email"] = email
    if display_name:
        payload["display_name"] = display_name
    if webauthn_user_id is not None:
        payload["webauthn_user_id"] = base64.b64encode(webauthn_user_id).decode("ascii")

    cache.set(
        _challenge_cache_key(challenge_id),
        json.dumps(payload),
        timeout=app_settings.WEBAUTHN_CHALLENGE_TIMEOUT_SECONDS,
    )
    return challenge_id


def retrieve_and_delete_challenge(*, challenge_id: str) -> dict:
    """Retrieve and atomically delete a WebAuthn challenge from the cache.

    Args:
        challenge_id: The UUID returned by store_challenge.

    Returns:
        The challenge payload dict with decoded bytes.

    Raises:
        ValidationError: If challenge is not found or expired.
    """
    import base64

    key = _challenge_cache_key(challenge_id)
    raw = cache.get(key)
    if raw is None:
        raise ValidationError(
            detail="Challenge not found or has expired.",
            code="challenge_invalid",
        )
    cache.delete(key)

    payload = json.loads(raw)
    payload["challenge"] = base64.b64decode(payload["challenge"])
    if "webauthn_user_id" in payload:
        payload["webauthn_user_id"] = base64.b64decode(payload["webauthn_user_id"])
    return payload


def passkey_register_options(
    *,
    email: str,
    display_name: str = "",
) -> dict:
    """Generate WebAuthn registration options for a new passkey user.

    Validates the email is not taken by a verified account, generates
    registration options via py_webauthn, stores the challenge, and
    returns the options JSON + challenge_id.

    Args:
        email: The email for the new account.
        display_name: Optional display name.

    Returns:
        Dict with "challenge_id" (str) and "options" (JSON string).

    Raises:
        ValidationError: If email belongs to a verified account.
    """
    from webauthn import generate_registration_options, options_to_json
    from webauthn.helpers.structs import (
        AuthenticatorSelectionCriteria,
        PublicKeyCredentialDescriptor,
        ResidentKeyRequirement,
        UserVerificationRequirement,
    )

    email = email.lower()

    # Check for existing verified account
    if User.objects.filter(email__iexact=email, is_email_verified=True).exists():
        raise ValidationError(
            detail="This email is already associated with a verified account.",
            code="email_already_verified",
        )

    # Collect existing credential IDs for exclude list (from unverified accounts)
    exclude_credentials: list[PublicKeyCredentialDescriptor] = []
    existing_user = User.objects.filter(email__iexact=email).first()
    if existing_user:
        from users.models import WebAuthnCredential

        for cred in WebAuthnCredential.objects.filter(user=existing_user):
            exclude_credentials.append(
                PublicKeyCredentialDescriptor(id=bytes(cred.credential_id))
            )

    webauthn_user_id = secrets.token_bytes(64)

    options = generate_registration_options(
        rp_id=app_settings.WEBAUTHN_RP_ID,
        rp_name=app_settings.WEBAUTHN_RP_NAME,
        user_name=email,
        user_id=webauthn_user_id,
        user_display_name=display_name or email,
        timeout=app_settings.WEBAUTHN_CHALLENGE_TIMEOUT_SECONDS * 1000,
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.REQUIRED,
            user_verification=UserVerificationRequirement.PREFERRED,
        ),
        exclude_credentials=exclude_credentials or None,
    )

    challenge_id = store_challenge(
        challenge=options.challenge,
        ceremony="registration",
        email=email,
        display_name=display_name,
        webauthn_user_id=webauthn_user_id,
    )

    options_json = options_to_json(options)

    logger.info("passkey_register_options_generated", email=email)

    return {
        "challenge_id": challenge_id,
        "options": options_json,
    }


@transaction.atomic
def passkey_register_complete(
    *,
    challenge_id: str,
    credential: dict,
) -> "CustomUser":
    """Complete passkey registration: verify attestation, create user + credential.

    Args:
        challenge_id: The challenge_id from the options step.
        credential: The WebAuthn attestation response from the client.

    Returns:
        The created CustomUser instance.

    Raises:
        ValidationError: If challenge is invalid/expired, credential verification
            fails, or email is already verified.
    """
    from webauthn import verify_registration_response

    challenge_data = retrieve_and_delete_challenge(challenge_id=challenge_id)

    if challenge_data.get("ceremony") != "registration":
        raise ValidationError(
            detail="Invalid challenge type.",
            code="challenge_invalid",
        )

    email = challenge_data["email"]
    display_name = challenge_data.get("display_name", "")
    webauthn_user_id = challenge_data["webauthn_user_id"]

    # Re-check email not verified (race condition guard)
    if User.objects.filter(email__iexact=email, is_email_verified=True).exists():
        raise ValidationError(
            detail="This email is already associated with a verified account.",
            code="email_already_verified",
        )

    # Verify the registration response
    try:
        verified = verify_registration_response(
            credential=credential,
            expected_challenge=challenge_data["challenge"],
            expected_rp_id=app_settings.WEBAUTHN_RP_ID,
            expected_origin=app_settings.WEBAUTHN_ORIGIN,
        )
    except Exception as e:
        logger.warning("passkey_register_verification_failed", error=str(e))
        raise ValidationError(
            detail="Passkey registration verification failed.",
            code="validation_error",
        ) from e

    # Supersede any existing unverified account
    existing_unverified = User.objects.filter(
        email__iexact=email, is_email_verified=False
    )
    if existing_unverified.exists():
        logger.info("passkey_register_superseded_unverified", email=email)
        existing_unverified.delete()

    # Create user with no password (passkey-only)
    user = User.objects.create_user(
        email=email,
        password=None,
        username=email,
    )

    Profile.objects.create(user=user, display_name=display_name)

    # Store the WebAuthn credential
    from users.models import WebAuthnCredential

    WebAuthnCredential.objects.create(
        user=user,
        credential_id=verified.credential_id,
        public_key=verified.credential_public_key,
        sign_count=verified.sign_count,
        webauthn_user_id=webauthn_user_id,
    )

    # Trigger email verification (same as password registration)
    token_obj = email_verification_token_create(user=user)
    email_verification_send(user=user, token_obj=token_obj)

    logger.info(
        "passkey_register_complete",
        user_id=user.id,
        email=user.email,
    )

    return user


def passkey_authenticate_options() -> dict:
    """Generate WebAuthn authentication options for discoverable credentials.

    No user identification is required — the authenticator presents a
    discoverable credential.

    Returns:
        Dict with "challenge_id" (str) and "options" (JSON string).
    """
    from webauthn import generate_authentication_options, options_to_json
    from webauthn.helpers.structs import UserVerificationRequirement

    options = generate_authentication_options(
        rp_id=app_settings.WEBAUTHN_RP_ID,
        timeout=app_settings.WEBAUTHN_CHALLENGE_TIMEOUT_SECONDS * 1000,
        allow_credentials=[],
        user_verification=UserVerificationRequirement.PREFERRED,
    )

    challenge_id = store_challenge(
        challenge=options.challenge,
        ceremony="authentication",
    )

    options_json = options_to_json(options)

    logger.info("passkey_authenticate_options_generated")

    return {
        "challenge_id": challenge_id,
        "options": options_json,
    }


@transaction.atomic
def passkey_authenticate_complete(
    *,
    challenge_id: str,
    credential: dict,
) -> dict:
    """Complete passkey authentication: verify assertion and issue JWT tokens.

    Args:
        challenge_id: The challenge_id from the options step.
        credential: The WebAuthn assertion response from the client.

    Returns:
        Dict with "access" and "refresh" JWT token strings.

    Raises:
        ValidationError: If challenge is invalid/expired, credential not found,
            credential disabled, sign count violation, or email not verified.
    """
    from webauthn import verify_authentication_response

    from users.selectors import passkey_credential_get_by_credential_id
    from users.serializers import CustomTokenObtainPairSerializer

    challenge_data = retrieve_and_delete_challenge(challenge_id=challenge_id)

    if challenge_data.get("ceremony") != "authentication":
        raise ValidationError(
            detail="Invalid challenge type.",
            code="challenge_invalid",
        )

    # Look up credential by credential_id from the assertion response
    import base64

    raw_id = credential.get("rawId") or credential.get("id", "")
    try:
        credential_id_bytes = base64.urlsafe_b64decode(raw_id + "==")
    except Exception:
        raise ValidationError(
            detail="Invalid credential format.",
            code="validation_error",
        )

    webauthn_credential = passkey_credential_get_by_credential_id(
        credential_id=credential_id_bytes,
    )

    if webauthn_credential is None:
        raise ValidationError(
            detail="Credential not registered.",
            code="credential_not_found",
        )

    if not webauthn_credential.is_enabled:
        logger.warning(
            "passkey_authenticate_credential_disabled",
            credential_id=webauthn_credential.pk,
            user_id=webauthn_credential.user_id,
        )
        raise ValidationError(
            detail="This credential has been disabled.",
            code="credential_disabled",
        )

    user = webauthn_credential.user

    if not user.is_email_verified:
        logger.info(
            "passkey_authenticate_email_not_verified",
            user_id=user.pk,
            email=user.email,
        )
        raise ValidationError(
            detail="Email address has not been verified.",
            code="email_not_verified",
        )

    # Verify the authentication response
    try:
        verified = verify_authentication_response(
            credential=credential,
            expected_challenge=challenge_data["challenge"],
            expected_rp_id=app_settings.WEBAUTHN_RP_ID,
            expected_origin=app_settings.WEBAUTHN_ORIGIN,
            credential_public_key=bytes(webauthn_credential.public_key),
            credential_current_sign_count=webauthn_credential.sign_count,
        )
    except Exception as e:
        # Sign count regression indicates possible credential cloning
        error_msg = str(e).lower()
        if "sign count" in error_msg or "counter" in error_msg:
            webauthn_credential.is_enabled = False
            webauthn_credential.save(update_fields=["is_enabled"])
            logger.warning(
                "passkey_credential_cloning_detected",
                credential_id=webauthn_credential.pk,
                user_id=user.pk,
                stored_sign_count=webauthn_credential.sign_count,
            )
            raise ValidationError(
                detail="Sign count violation — credential has been disabled.",
                code="credential_cloned",
            ) from e

        logger.warning("passkey_authenticate_verification_failed", error=str(e))
        raise ValidationError(
            detail="Passkey authentication verification failed.",
            code="validation_error",
        ) from e

    # Update the sign count
    webauthn_credential.sign_count = verified.new_sign_count
    webauthn_credential.save(update_fields=["sign_count"])

    # Issue JWT tokens
    token = CustomTokenObtainPairSerializer.get_token(user)

    logger.info(
        "passkey_authenticate_complete",
        user_id=user.pk,
        email=user.email,
        credential_id=webauthn_credential.pk,
    )

    return {
        "access": str(token.access_token),
        "refresh": str(token),
    }


def passkey_add_options(
    *,
    user: "CustomUser",
    device_label: str = "",
) -> dict:
    """Generate WebAuthn registration options to add a passkey to an existing account.

    Args:
        user: The authenticated user.
        device_label: Optional label for the new passkey.

    Returns:
        Dict with "challenge_id" (str) and "options" (JSON string).

    Raises:
        ValidationError: If email not verified or max credentials reached.
    """
    from webauthn import generate_registration_options, options_to_json
    from webauthn.helpers.structs import (
        AuthenticatorSelectionCriteria,
        PublicKeyCredentialDescriptor,
        ResidentKeyRequirement,
        UserVerificationRequirement,
    )

    from users.models import WebAuthnCredential

    if not user.is_email_verified:
        raise ValidationError(
            detail="Email address has not been verified.",
            code="email_not_verified",
        )

    existing_credentials = WebAuthnCredential.objects.filter(user=user)
    if existing_credentials.count() >= app_settings.WEBAUTHN_MAX_CREDENTIALS_PER_USER:
        raise ValidationError(
            detail="Maximum number of passkeys reached.",
            code="max_credentials_reached",
        )

    # Build exclude list from existing credentials
    exclude_credentials = [
        PublicKeyCredentialDescriptor(id=bytes(cred.credential_id))
        for cred in existing_credentials
    ]

    # Reuse the webauthn_user_id from the user's first credential, or generate new
    first_cred = existing_credentials.first()
    if first_cred:
        webauthn_user_id = bytes(first_cred.webauthn_user_id)
    else:
        webauthn_user_id = secrets.token_bytes(64)

    options = generate_registration_options(
        rp_id=app_settings.WEBAUTHN_RP_ID,
        rp_name=app_settings.WEBAUTHN_RP_NAME,
        user_name=user.email,
        user_id=webauthn_user_id,
        user_display_name=device_label or user.email,
        timeout=app_settings.WEBAUTHN_CHALLENGE_TIMEOUT_SECONDS * 1000,
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.REQUIRED,
            user_verification=UserVerificationRequirement.PREFERRED,
        ),
        exclude_credentials=exclude_credentials or None,
    )

    challenge_id = store_challenge(
        challenge=options.challenge,
        ceremony="add",
        email=user.email,
        display_name=device_label,
        webauthn_user_id=webauthn_user_id,
    )

    options_json = options_to_json(options)

    logger.info("passkey_add_options_generated", user_id=user.pk)

    return {
        "challenge_id": challenge_id,
        "options": options_json,
    }


@transaction.atomic
def passkey_add_complete(
    *,
    user: "CustomUser",
    challenge_id: str,
    credential: dict,
) -> "WebAuthnCredential":
    """Complete adding a passkey to an existing account.

    Args:
        user: The authenticated user.
        challenge_id: The challenge_id from the options step.
        credential: The WebAuthn attestation response from the client.
        device_label: Optional label for the new passkey.

    Returns:
        The created WebAuthnCredential instance.

    Raises:
        ValidationError: If challenge is invalid/expired, credential verification
            fails, email not verified, or max credentials reached.
    """
    from webauthn import verify_registration_response

    from users.models import WebAuthnCredential

    if not user.is_email_verified:
        raise ValidationError(
            detail="Email address has not been verified.",
            code="email_not_verified",
        )

    if (
        WebAuthnCredential.objects.filter(user=user).count()
        >= app_settings.WEBAUTHN_MAX_CREDENTIALS_PER_USER
    ):
        raise ValidationError(
            detail="Maximum number of passkeys reached.",
            code="max_credentials_reached",
        )

    challenge_data = retrieve_and_delete_challenge(challenge_id=challenge_id)

    if challenge_data.get("ceremony") != "add":
        raise ValidationError(
            detail="Invalid challenge type.",
            code="challenge_invalid",
        )

    try:
        verified = verify_registration_response(
            credential=credential,
            expected_challenge=challenge_data["challenge"],
            expected_rp_id=app_settings.WEBAUTHN_RP_ID,
            expected_origin=app_settings.WEBAUTHN_ORIGIN,
        )
    except Exception as e:
        logger.warning("passkey_add_verification_failed", error=str(e), user_id=user.pk)
        raise ValidationError(
            detail="Passkey verification failed.",
            code="validation_error",
        ) from e

    device_label = challenge_data.get("display_name", "")

    webauthn_credential = WebAuthnCredential.objects.create(
        user=user,
        credential_id=verified.credential_id,
        public_key=verified.credential_public_key,
        sign_count=verified.sign_count,
        webauthn_user_id=challenge_data["webauthn_user_id"],
        device_label=device_label,
    )

    logger.info(
        "passkey_add_complete",
        user_id=user.pk,
        credential_id=webauthn_credential.pk,
        device_label=device_label,
    )

    return webauthn_credential


# =============================================================================
# User Story 4: Passkey Management (List / Remove)
# =============================================================================


def passkey_credential_remove(
    *,
    user: "CustomUser",
    credential_id: int,
) -> None:
    """Remove a passkey credential from a user's account.

    Verifies the credential belongs to the user and prevents removal if it is
    the user's last authentication method (no password and only one passkey).

    Args:
        user: The authenticated user.
        credential_id: The database PK of the credential to remove.

    Raises:
        ValidationError: If credential not found, doesn't belong to user,
            or is the last authentication method.
    """
    from users.models import WebAuthnCredential

    credential = WebAuthnCredential.objects.filter(pk=credential_id, user=user).first()

    if credential is None:
        raise ValidationError(
            detail="Credential not found.",
            code="not_found",
        )

    has_password = user.has_usable_password()
    passkey_count = WebAuthnCredential.objects.filter(user=user).count()

    if not has_password and passkey_count <= 1:
        raise ValidationError(
            detail="Cannot remove last passkey when no password is set.",
            code="last_auth_method",
        )

    credential_pk = credential.pk
    credential.delete()

    logger.info(
        "passkey_credential_removed",
        user_id=user.pk,
        credential_id=credential_pk,
    )
