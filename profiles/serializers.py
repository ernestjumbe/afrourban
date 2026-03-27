"""Profile serializers for input and output data."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from rest_framework import serializers

from profiles.models import Profile


class ProfileInputSerializer(serializers.Serializer):
    """Input serializer for profile updates.

    All fields are optional for PATCH operations.
    Preferences are partially merged with existing values.
    """

    display_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="Public display name (max 100 characters)",
    )
    bio = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="Short biography (max 500 characters)",
    )
    phone_number = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        help_text="Contact phone number",
    )
    date_of_birth = serializers.DateField(
        required=False,
        allow_null=True,
        help_text="Birth date (YYYY-MM-DD format)",
    )
    preferences = serializers.JSONField(
        required=False,
        help_text="User preferences (partial update merged with existing)",
    )

    def validate_date_of_birth(self, value: date | None) -> date | None:
        """Validate date of birth constraints.

        Args:
            value: Date to validate.

        Returns:
            Validated date or None.

        Raises:
            serializers.ValidationError: If date is invalid.
        """
        if value is None:
            return value

        if value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")

        min_date = date.today() - timedelta(days=120 * 365)
        if value < min_date:
            raise serializers.ValidationError(
                "Date of birth cannot be more than 120 years ago."
            )

        return value


class ProfileOutputSerializer(serializers.Serializer):
    """Full profile output serializer for owner view.

    Includes all profile fields plus user email.
    Used for GET /api/profiles/me/ and PATCH response.
    """

    user_id = serializers.IntegerField(source="user.id", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    display_name = serializers.CharField(allow_blank=True, read_only=True)
    bio = serializers.CharField(allow_blank=True, read_only=True)
    avatar = serializers.SerializerMethodField()
    phone_number = serializers.CharField(allow_blank=True, read_only=True)
    date_of_birth = serializers.DateField(allow_null=True, read_only=True)
    age = serializers.IntegerField(read_only=True, allow_null=True)
    age_verification_status = serializers.CharField(read_only=True)
    age_verified_at = serializers.DateTimeField(read_only=True, allow_null=True)
    preferences = serializers.JSONField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def get_avatar(self, obj: Profile) -> str | None:
        """Return full avatar URL or None.

        Args:
            obj: Profile instance.

        Returns:
            Absolute URL to avatar or None if no avatar.
        """
        if obj.avatar:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None


class ProfilePublicOutputSerializer(serializers.Serializer):
    """Public profile output serializer.

    Limited fields for viewing other users' profiles.
    Used for GET /api/profiles/{user_id}/.

    Note: date_of_birth is NOT included (privacy compliance FR-013).
    Only age and age_verified are exposed.
    """

    user_id = serializers.IntegerField(source="user.id", read_only=True)
    display_name = serializers.CharField(allow_blank=True, read_only=True)
    bio = serializers.CharField(allow_blank=True, read_only=True)
    avatar = serializers.SerializerMethodField()
    age = serializers.IntegerField(read_only=True, allow_null=True)
    age_verified = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    def get_avatar(self, obj: Profile) -> str | None:
        """Return full avatar URL or None.

        Args:
            obj: Profile instance.

        Returns:
            Absolute URL to avatar or None if no avatar.
        """
        if obj.avatar:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None


class AvatarUploadSerializer(serializers.Serializer):
    """Input serializer for avatar upload.

    Validates file type (JPEG, PNG, WebP) and size (max 5MB).
    """

    ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png", "image/webp"]
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

    avatar = serializers.ImageField(
        required=True,
        help_text="Profile picture (JPEG, PNG, or WebP, max 5MB)",
    )

    def validate_avatar(self, value: Any) -> Any:
        """Validate avatar file type and size.

        Args:
            value: Uploaded file.

        Returns:
            Validated file.

        Raises:
            ValidationError: If file type or size is invalid.
        """
        # Check file size
        if value.size > self.MAX_FILE_SIZE:
            raise serializers.ValidationError("File size exceeds 5MB limit.")

        # Check content type
        content_type = value.content_type
        if content_type not in self.ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError(
                "Unsupported file format. Use JPEG, PNG, or WebP."
            )

        return value


# =============================================================================
# Policy Serializers (Phase 7: User Story 5)
# =============================================================================


class PolicyOutputSerializer(serializers.Serializer):
    """Output serializer for Policy model.

    Used in role detail and user policy listings.
    """

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True, allow_blank=True)
    conditions = serializers.JSONField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class PolicySummarySerializer(serializers.Serializer):
    """Summary serializer for Policy in role listings.

    Minimal fields for embedding in role responses.
    """

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)


class PolicyCheckOutputSerializer(serializers.Serializer):
    """Output serializer for policy check response.

    Returns whether the authenticated user passes a specific policy,
    with reason and message on failure.
    """

    policy_id = serializers.IntegerField(read_only=True)
    policy_name = serializers.CharField(read_only=True)
    passed = serializers.BooleanField(read_only=True)
    reason = serializers.CharField(read_only=True, allow_null=True, default=None)
    message = serializers.CharField(read_only=True, allow_null=True, default=None)
    evaluated_at = serializers.DateTimeField(read_only=True)


class AvatarOutputSerializer(serializers.Serializer):
    """Output serializer for avatar upload response."""

    avatar = serializers.URLField(read_only=True)
    message = serializers.CharField(read_only=True)
