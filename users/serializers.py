"""User serializers for registration and authentication."""

from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from users.claims import build_token_claims, get_user_policies

User = get_user_model()


class RegisterInputSerializer(serializers.Serializer):
    """Input serializer for user registration.

    Validates registration data including email uniqueness
    and password confirmation matching.
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
    display_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="Optional public display name",
    )

    def validate_email(self, value: str) -> str:
        """Validate email is not already in use."""
        email = value.lower()
        if User.objects.filter(email__iexact=email).exists():
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
        """Validate passwords match."""
        if attrs.get("password") != attrs.get("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs


class ProfileOutputSerializer(serializers.Serializer):
    """Output serializer for profile data in user responses."""

    display_name = serializers.CharField(allow_blank=True)
    avatar = serializers.ImageField(allow_null=True)


class UserOutputSerializer(serializers.Serializer):
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


class TokenUserSerializer(serializers.Serializer):
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
            RefreshToken with custom claims.
        """
        token = super().get_token(user)

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
        data = super().validate(attrs)

        # Add user data to response
        policies = get_user_policies(self.user)
        data["user"] = {
            "id": self.user.pk,
            "email": self.user.email,
            "is_staff": self.user.is_staff,
            "policies": policies,
        }

        return data


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout endpoint."""

    refresh = serializers.CharField(help_text="The refresh token to blacklist")

    def validate_refresh(self, value: str) -> str:
        """Validate the refresh token."""
        try:
            RefreshToken(value)
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


class AdminUserListSerializer(serializers.Serializer):
    """Serializer for user list in admin view.

    Returns minimal user data for list display.
    """

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


class AdminUserDetailSerializer(serializers.Serializer):
    """Serializer for user detail in admin view.

    Returns full user data including profile, roles, and permissions.
    """

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


class UserActivationOutputSerializer(serializers.Serializer):
    """Output serializer for user activation/deactivation."""

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
