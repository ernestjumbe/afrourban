"""User serializers for registration and authentication."""

from __future__ import annotations

from typing import Any, cast

import structlog
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from users.claims import build_token_claims, get_age_verification, get_user_policies
from users.services import (
    log_email_visibility_outcome,
    username_is_taken,
    validate_username_format,
)

User = get_user_model()
logger = structlog.get_logger(__name__)


def _viewer_id(*, viewer: Any) -> int | None:
    return cast(int | None, getattr(viewer, "pk", None))


def is_user_object_owned(*, viewer: Any, subject_user_id: int | None) -> bool:
    """Return True when viewer owns the serialized user object."""

    viewer_user_id = _viewer_id(viewer=viewer)
    return (
        viewer_user_id is not None
        and subject_user_id is not None
        and viewer_user_id == subject_user_id
    )


def can_view_user_email(
    *,
    viewer: Any,
    subject_user_id: int | None,
    allow_staff_non_owned: bool = True,
) -> bool:
    """Return True when email should be visible for this viewer/subject pair."""

    owned = is_user_object_owned(viewer=viewer, subject_user_id=subject_user_id)
    if owned:
        return True

    viewer_is_staff = bool(getattr(viewer, "is_staff", False))
    viewer_is_superuser = bool(getattr(viewer, "is_superuser", False))
    return allow_staff_non_owned and (viewer_is_staff or viewer_is_superuser)


def project_user_email_for_viewer(
    *,
    email: str,
    viewer: Any,
    subject_user_id: int | None,
    allow_staff_non_owned: bool = True,
) -> str | None:
    """Return email when visible for the viewer, otherwise None."""

    owned = is_user_object_owned(viewer=viewer, subject_user_id=subject_user_id)
    viewer_is_staff = bool(getattr(viewer, "is_staff", False))
    email_visible = can_view_user_email(
        viewer=viewer,
        subject_user_id=subject_user_id,
        allow_staff_non_owned=allow_staff_non_owned,
    )

    log_email_visibility_outcome(
        outcome="email_visible" if email_visible else "email_redacted",
        viewer_user_id=_viewer_id(viewer=viewer),
        subject_user_id=subject_user_id,
        viewer_is_staff=viewer_is_staff,
        is_owned=owned,
        email_visible=email_visible,
        source="users.serializers",
    )

    return email if email_visible else None


def redact_user_email_in_payload(
    *,
    payload: dict[str, Any],
    viewer: Any,
    subject_user_id: int | None,
    email_key: str = "email",
    allow_staff_non_owned: bool = True,
) -> dict[str, Any]:
    """Apply ownership/role-based email visibility to a serialized payload."""

    if email_key not in payload:
        return payload

    projected_email = project_user_email_for_viewer(
        email=cast(str, payload[email_key]),
        viewer=viewer,
        subject_user_id=subject_user_id,
        allow_staff_non_owned=allow_staff_non_owned,
    )

    if projected_email is not None:
        return payload

    redacted_payload = dict(payload)
    redacted_payload.pop(email_key, None)
    return redacted_payload


class EmailVisibilitySerializerMixin:
    """Apply ownership-aware email redaction to serializer payloads."""

    email_visibility_allow_staff_non_owned = False
    email_visibility_email_key = "email"

    def _email_visibility_subject_user_id(self, instance: Any) -> int | None:
        subject_user_id = cast(int | None, getattr(instance, "pk", None))
        if subject_user_id is not None:
            return subject_user_id

        subject_user_id = cast(int | None, getattr(instance, "user_id", None))
        if subject_user_id is not None:
            return subject_user_id

        subject_user = getattr(instance, "user", None)
        return cast(int | None, getattr(subject_user, "pk", None))

    def to_representation(self, instance: Any) -> dict[str, Any]:
        serializer_self = cast(serializers.Serializer, self)
        payload = cast(
            dict[str, Any],
            serializers.Serializer.to_representation(serializer_self, instance),
        )
        request = serializer_self.context.get("request")
        viewer = serializer_self.context.get("email_visibility_viewer")
        if viewer is None and request is not None:
            viewer = getattr(request, "user", None)

        if viewer is None:
            return payload

        return redact_user_email_in_payload(
            payload=payload,
            viewer=viewer,
            subject_user_id=self._email_visibility_subject_user_id(instance),
            email_key=self.email_visibility_email_key,
            allow_staff_non_owned=self.email_visibility_allow_staff_non_owned,
        )


class RegisterInputSerializer(serializers.Serializer):
    """Input serializer for user registration.

    Validates registration data including email uniqueness,
    username requirements, and password confirmation matching.
    """

    email = serializers.EmailField(
        max_length=255,
        help_text="User's email address (used as login identifier)",
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
        help_text="User's password (min 8 characters)",
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        help_text="Password confirmation (must match password)",
    )
    username = serializers.CharField(
        max_length=User.USERNAME_INPUT_MAX_LENGTH,
        help_text=(
            "Required account username. Must be 3-30 characters, contain at least "
            "one letter, not start with '.', and use only letters, numbers, '_' "
            "or '.'."
        ),
    )
    display_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="Optional public display name",
    )

    def validate_email(self, value: str) -> str:
        """Validate email is not already in use by a verified account."""
        email = value.lower()
        if User.objects.filter(email__iexact=email, is_email_verified=True).exists():
            raise serializers.ValidationError("This email is already in use.")
        return email

    def validate_password(self, value: str) -> str:
        """Validate password meets Django's password requirements."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages)) from e
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate passwords match and username is available."""
        if attrs.get("password") != attrs.get("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )

        username = validate_username_format(username=attrs["username"])
        existing_unverified = User.objects.filter(
            email__iexact=attrs["email"],
            is_email_verified=False,
        ).only("id")
        existing_unverified_user = existing_unverified.first()
        exclude_user_id = (
            existing_unverified_user.pk
            if existing_unverified_user is not None
            else None
        )

        if username_is_taken(username=username, exclude_user_id=exclude_user_id):
            raise serializers.ValidationError(
                {"username": ["This username is already in use."]}
            )

        attrs["username"] = username
        return attrs


class VerifyEmailInputSerializer(serializers.Serializer):
    """Input serializer for email verification."""

    token = serializers.CharField()


class ResendVerificationEmailInputSerializer(serializers.Serializer):
    """Input serializer for resending a verification email."""

    email = serializers.EmailField()


class ProfileOutputSerializer(serializers.Serializer):
    """Output serializer for profile data in user responses."""

    display_name = serializers.CharField(allow_blank=True)
    avatar = serializers.ImageField(allow_null=True)


class UserOutputSerializer(EmailVisibilitySerializerMixin, serializers.Serializer):
    """Output serializer for user data after registration.

    Returns user info along with nested profile data.
    """

    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    profile = ProfileOutputSerializer(read_only=True)
    created_at = serializers.DateTimeField(source="date_joined", read_only=True)


class UserPoliciesSerializer(serializers.Serializer):
    """Serializer for user policies in token response."""

    roles = serializers.ListField(child=serializers.CharField())
    permissions = serializers.ListField(child=serializers.CharField())


class TokenUserSerializer(EmailVisibilitySerializerMixin, serializers.Serializer):
    """Serializer for user data in token response."""

    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    policies = UserPoliciesSerializer(read_only=True)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with user data and policies.

    Extends the default TokenObtainPairSerializer to:
    1. Use email instead of username
    2. Include user data in response
    3. Embed policies as private claims in the token
    """

    username_field = "email"

    @classmethod
    def get_token(cls, user) -> RefreshToken:
        """Get token with custom claims embedded.

        Args:
            user: The authenticated user.

        Returns:
            JWT token with custom claims.
        """
        token = cast(RefreshToken, super().get_token(user))

        # Add custom claims to token payload
        claims = build_token_claims(user)
        for key, value in claims.items():
            token[key] = value

        return token

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate credentials and build response with user data.

        Args:
            attrs: Input attributes (email, password).

        Returns:
            Token data with user information.
        """
        data: dict[str, Any] = dict(super().validate(attrs))

        if not self.user.is_email_verified:
            logger.info(
                "email_verification_blocked_login",
                user_id=self.user.pk,
                email=self.user.email,
            )
            raise AuthenticationFailed(
                detail="Email address has not been verified.",
                code="email_not_verified",
            )

        # Add user data to response
        policies = get_user_policies(self.user)
        age_verification = get_age_verification(self.user)

        user_data = {
            "id": self.user.pk,
            "email": self.user.email,
            "is_staff": self.user.is_staff,
            "policies": policies,
        }

        if age_verification is not None:
            user_data["age_verification"] = age_verification

        data["user"] = user_data

        return data


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout endpoint."""

    refresh = serializers.CharField(help_text="The refresh token to blacklist")

    def validate_refresh(self, value: str) -> str:
        """Validate the refresh token."""
        try:
            RefreshToken(cast(Any, value))
        except Exception as e:
            raise serializers.ValidationError("Invalid refresh token.") from e
        return value


# =============================================================================
# Admin Serializers (Phase 6: User Story 4)
# =============================================================================


class RoleSerializer(serializers.Serializer):
    """Serializer for role (Django Group) in user responses."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class AdminUserListSerializer(EmailVisibilitySerializerMixin, serializers.Serializer):
    """Serializer for user list in admin view.

    Returns minimal user data for list display.
    """

    email_visibility_allow_staff_non_owned = True

    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    display_name = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True, allow_null=True)
    roles = serializers.SerializerMethodField()

    def get_display_name(self, obj: Any) -> str:
        """Get display name from profile."""
        if hasattr(obj, "profile") and obj.profile:
            return obj.profile.display_name or ""
        return ""

    def get_roles(self, obj: Any) -> list[str]:
        """Get role names from user's groups."""
        return [group.name for group in obj.groups.all()]


class AdminProfileSerializer(serializers.Serializer):
    """Serializer for profile data in admin user detail."""

    display_name = serializers.CharField(allow_blank=True, read_only=True)
    bio = serializers.CharField(allow_blank=True, read_only=True)
    avatar = serializers.SerializerMethodField()
    phone_number = serializers.CharField(allow_blank=True, read_only=True)
    age_verification_status = serializers.CharField(read_only=True)
    age_verified_at = serializers.DateTimeField(read_only=True, allow_null=True)

    def get_avatar(self, obj: Any) -> str | None:
        """Get avatar URL."""
        if obj.avatar:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None


class PermissionSerializer(serializers.Serializer):
    """Serializer for permission data."""

    id = serializers.IntegerField(read_only=True)
    codename = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)


class PolicySerializer(serializers.Serializer):
    """Serializer for policy data (placeholder for Phase 7)."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class AdminUserDetailSerializer(EmailVisibilitySerializerMixin, serializers.Serializer):
    """Serializer for user detail in admin view.

    Returns full user data including profile, roles, and permissions.
    """

    email_visibility_allow_staff_non_owned = True

    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True, allow_null=True)
    profile = AdminProfileSerializer(read_only=True)
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    policies = serializers.SerializerMethodField()

    def get_roles(self, obj: Any) -> list[dict]:
        """Get roles with IDs and names."""
        return [{"id": g.id, "name": g.name} for g in obj.groups.all()]

    def get_permissions(self, obj: Any) -> list[str]:
        """Get all permission codenames."""
        perms = set()
        for p in obj.user_permissions.all():
            perms.add(p.codename)
        for g in obj.groups.all():
            for p in g.permissions.all():
                perms.add(p.codename)
        return sorted(perms)

    def get_policies(self, obj: Any) -> list[dict]:
        """Get policies (placeholder for Phase 7)."""
        return []


class AdminUserUpdateInputSerializer(serializers.Serializer):
    """Input serializer for updating user via admin."""

    is_staff = serializers.BooleanField(required=False)
    roles = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of role (group) IDs to assign",
    )


class UserActivationOutputSerializer(EmailVisibilitySerializerMixin, serializers.Serializer):
    """Output serializer for user activation/deactivation."""

    email_visibility_allow_staff_non_owned = True

    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    message = serializers.CharField(read_only=True)


class PermissionsInputSerializer(serializers.Serializer):
    """Input serializer for setting user permissions."""

    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of permission IDs to assign",
    )


class PermissionsOutputSerializer(serializers.Serializer):
    """Output serializer for user permissions response."""

    user_id = serializers.IntegerField(read_only=True)
    direct_permissions = serializers.ListField(read_only=True)
    role_permissions = serializers.ListField(read_only=True)
    effective_permissions = serializers.ListField(
        child=serializers.CharField(), read_only=True
    )
    message = serializers.CharField(read_only=True, required=False)


# =============================================================================
# Role Serializers (Phase 7: User Story 5)
# =============================================================================


class RoleListSerializer(serializers.Serializer):
    """Serializer for role list endpoint.

    Returns role summary with user and permission counts.
    """

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    user_count = serializers.IntegerField(read_only=True)
    permission_count = serializers.IntegerField(read_only=True)


class RoleDetailSerializer(serializers.Serializer):
    """Serializer for role detail endpoint.

    Returns full role data with permissions and policies.
    """

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    permissions = PermissionSerializer(many=True, read_only=True)
    policies = serializers.ListField(read_only=True)
    user_count = serializers.IntegerField(read_only=True)


class RoleCreateInputSerializer(serializers.Serializer):
    """Input serializer for creating a new role.

    Validates that name is unique and permissions exist.
    """

    name = serializers.CharField(
        max_length=150,
        help_text="Unique role name",
    )
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list,
        help_text="List of permission IDs to assign",
    )

    def validate_name(self, value: str) -> str:
        """Validate role name is unique."""
        from django.contrib.auth.models import Group

        if Group.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A role with this name already exists.")
        return value


class RoleUpdateInputSerializer(serializers.Serializer):
    """Input serializer for updating a role.

    All fields are optional for PATCH operations.
    """

    name = serializers.CharField(
        max_length=150,
        required=False,
        help_text="New role name",
    )
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of permission IDs to assign (replaces existing)",
    )


class RoleOutputSerializer(serializers.Serializer):
    """Output serializer for role create/update responses.

    Returns role data with embedded permissions.
    """

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    permissions = PermissionSerializer(many=True, read_only=True)


# =============================================================================
# Password Management Serializers (Phase 8: User Story 6)
# =============================================================================


class PasswordResetRequestSerializer(serializers.Serializer):
    """Input serializer for password reset request.

    Validates email format. Does not check if email exists
    to prevent email enumeration attacks.
    """

    email = serializers.EmailField(
        help_text="Email address for the account to reset password"
    )


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Input serializer for password reset confirmation.

    Validates token, new password, and password confirmation.
    """

    token = serializers.CharField(help_text="Password reset token from email")
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
        help_text="New password (min 8 characters)",
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        help_text="New password confirmation (must match password)",
    )

    def validate_password(self, value: str) -> str:
        """Validate password meets Django's password requirements."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages)) from e
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate passwords match."""
        if attrs.get("password") != attrs.get("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """Input serializer for authenticated password change.

    Validates old password, new password, and confirmation.
    """

    old_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        help_text="Current password",
    )
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
        help_text="New password (min 8 characters)",
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        help_text="New password confirmation (must match new_password)",
    )

    def validate_new_password(self, value: str) -> str:
        """Validate new password meets Django's password requirements."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages)) from e
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate new passwords match."""
        if attrs.get("new_password") != attrs.get("new_password_confirm"):
            raise serializers.ValidationError(
                {"new_password_confirm": "Passwords do not match."}
            )
        return attrs


class UsernameChangeInputSerializer(serializers.Serializer):
    """Input serializer for authenticated username changes."""

    username = serializers.CharField(
        max_length=User.USERNAME_INPUT_MAX_LENGTH,
        help_text=(
            "New account username. Must be 3-30 characters, contain at least "
            "one letter, not start with '.', and use only letters, numbers, '_' "
            "or '.'."
        ),
    )


class UsernameChangeOutputSerializer(serializers.Serializer):
    """Output serializer for successful username changes."""

    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    cooldown_days = serializers.IntegerField(read_only=True)
    next_allowed_at = serializers.DateTimeField(read_only=True)


# =============================================================================
# Passkey Serializers (US1: Registration)
# =============================================================================


class PasskeyRegisterOptionsInputSerializer(serializers.Serializer):
    """Input serializer for passkey registration options."""

    email = serializers.EmailField(
        help_text="Email address for the new account",
    )
    display_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        default="",
        help_text="Optional display name (max 100 chars)",
    )


class PasskeyRegisterOptionsOutputSerializer(serializers.Serializer):
    """Output serializer for passkey registration options."""

    challenge_id = serializers.CharField()
    options = serializers.JSONField()


class PasskeyRegisterCompleteInputSerializer(serializers.Serializer):
    """Input serializer for passkey registration completion."""

    challenge_id = serializers.UUIDField(
        help_text="Challenge ID from options response",
    )
    credential = serializers.JSONField(
        help_text="WebAuthn attestation response from navigator.credentials.create()",
    )


class PasskeyRegisterCompleteOutputSerializer(serializers.Serializer):
    """Output serializer for passkey registration completion."""

    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    is_email_verified = serializers.BooleanField(read_only=True)
    message = serializers.CharField(read_only=True)


# =============================================================================
# Passkey Serializers (US2: Authentication)
# =============================================================================


class PasskeyAuthenticateOptionsOutputSerializer(serializers.Serializer):
    """Output serializer for passkey authentication options."""

    challenge_id = serializers.CharField()
    options = serializers.JSONField()


class PasskeyAuthenticateCompleteInputSerializer(serializers.Serializer):
    """Input serializer for passkey authentication completion."""

    challenge_id = serializers.UUIDField(
        help_text="Challenge ID from options response",
    )
    credential = serializers.JSONField(
        help_text="WebAuthn assertion response from navigator.credentials.get()",
    )


class PasskeyAuthenticateCompleteOutputSerializer(serializers.Serializer):
    """Output serializer for passkey authentication completion."""

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)


# =============================================================================
# Passkey Serializers (US3: Add Passkey to Existing Account)
# =============================================================================


class PasskeyAddOptionsInputSerializer(serializers.Serializer):
    """Input serializer for adding a passkey to an existing account."""

    device_label = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        default="",
        help_text="Optional label for the new passkey (max 100 chars)",
    )


class PasskeyAddOptionsOutputSerializer(serializers.Serializer):
    """Output serializer for passkey add options."""

    challenge_id = serializers.CharField()
    options = serializers.JSONField()


class PasskeyAddCompleteInputSerializer(serializers.Serializer):
    """Input serializer for completing passkey addition."""

    challenge_id = serializers.UUIDField(
        help_text="Challenge ID from options response",
    )
    credential = serializers.JSONField(
        help_text="WebAuthn attestation response from navigator.credentials.create()",
    )


class PasskeyAddCompleteOutputSerializer(serializers.Serializer):
    """Output serializer for passkey addition completion."""

    id = serializers.IntegerField(read_only=True)
    device_label = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    is_enabled = serializers.BooleanField(read_only=True)


# =============================================================================
# User Story 4: Passkey Management (List / Remove)
# =============================================================================


class PasskeyCredentialListOutputSerializer(serializers.Serializer):
    """Output serializer for listing passkey credentials."""

    id = serializers.IntegerField(read_only=True)
    device_label = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    is_enabled = serializers.BooleanField(read_only=True)
