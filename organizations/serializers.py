"""Serializers for organization API input and output."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError

from organizations.models import Organization, OrganizationType
from organizations.services import validate_organization_image


class OrganizationCreateInputSerializer(serializers.Serializer):
    """Input serializer for organization create requests."""

    name = serializers.CharField(
        max_length=Organization.NAME_MAX_LENGTH,
        trim_whitespace=True,
        help_text="Public organization name.",
    )
    description = serializers.CharField(
        trim_whitespace=True,
        help_text="Public organization description or bio.",
    )
    organization_type = serializers.ChoiceField(
        choices=OrganizationType.choices,
        help_text="Primary organization category.",
    )
    is_online_only = serializers.BooleanField(
        help_text="Whether the organization operates exclusively online.",
    )
    physical_address = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        trim_whitespace=True,
        help_text="Physical address when the organization is not online-only.",
    )


class OrganizationListQuerySerializer(serializers.Serializer):
    """Query serializer for organization collection reads."""

    owner_scope = serializers.ChoiceField(
        choices=(("all", "all"), ("mine", "mine")),
        required=False,
        default="all",
        help_text="Whether to show all organizations or only the viewer's own.",
    )
    organization_type = serializers.ChoiceField(
        choices=OrganizationType.choices,
        required=False,
        allow_null=True,
        help_text="Filter to one organization type.",
    )
    is_online_only = serializers.BooleanField(
        required=False,
        help_text="Filter by online-only presence mode.",
    )
    search = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Case-insensitive search over organization name and description.",
    )
    ordering = serializers.CharField(
        required=False,
        default="-created_at",
        help_text="Requested ordering. Unsupported values fall back to -created_at.",
    )
    page = serializers.IntegerField(
        required=False,
        default=1,
        min_value=1,
        help_text="Requested page number.",
    )
    page_size = serializers.IntegerField(
        required=False,
        default=20,
        min_value=1,
        help_text="Requested page size. Values above 100 are clamped.",
    )

    def validate_page_size(self, value: int) -> int:
        """Clamp page size to the documented maximum."""

        return min(value, 100)


class OrganizationSummarySerializer(serializers.Serializer):
    """Output serializer for organization collection and detail payloads."""

    id = serializers.IntegerField(read_only=True)
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    organization_type = serializers.CharField(read_only=True)
    is_online_only = serializers.BooleanField(read_only=True)
    physical_address = serializers.CharField(read_only=True, allow_null=True)
    logo_url = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def get_logo_url(self, obj: Organization) -> str | None:
        """Return the absolute logo URL when available."""

        return _build_media_url(self.context.get("request"), obj.logo)

    def get_cover_image_url(self, obj: Organization) -> str | None:
        """Return the absolute cover-image URL when available."""

        return _build_media_url(self.context.get("request"), obj.cover_image)


class OrganizationDetailSerializer(OrganizationSummarySerializer):
    """Output serializer for organization detail and mutation responses."""


class OrganizationListResponseSerializer(serializers.Serializer):
    """Pagination envelope serializer for organization collection responses."""

    count = serializers.IntegerField(read_only=True)
    next = serializers.CharField(read_only=True, allow_null=True)
    previous = serializers.CharField(read_only=True, allow_null=True)
    results = OrganizationSummarySerializer(many=True, read_only=True)


class OrganizationUpdateInputSerializer(serializers.Serializer):
    """Input serializer for organization patch requests."""

    name = serializers.CharField(
        max_length=Organization.NAME_MAX_LENGTH,
        required=False,
        trim_whitespace=True,
        help_text="Updated public organization name.",
    )
    description = serializers.CharField(
        required=False,
        trim_whitespace=True,
        help_text="Updated public organization description or bio.",
    )
    organization_type = serializers.ChoiceField(
        choices=OrganizationType.choices,
        required=False,
        help_text="Updated primary organization category.",
    )
    is_online_only = serializers.BooleanField(
        required=False,
        help_text="Whether the organization operates exclusively online.",
    )
    physical_address = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        trim_whitespace=True,
        help_text="Updated physical address when the organization is not online-only.",
    )


class OrganizationLogoUploadSerializer(serializers.Serializer):
    """Input serializer for logo uploads."""

    logo = serializers.FileField(
        required=True,
        help_text="Organization logo (JPEG, PNG, or WebP, max 5MB).",
    )

    def validate_logo(self, value: Any) -> Any:
        """Validate logo uploads against shared image rules."""

        return _validate_branding_image(value)


class OrganizationCoverUploadSerializer(serializers.Serializer):
    """Input serializer for cover-image uploads."""

    cover_image = serializers.FileField(
        required=True,
        help_text="Organization cover image (JPEG, PNG, or WebP, max 5MB).",
    )

    def validate_cover_image(self, value: Any) -> Any:
        """Validate cover-image uploads against shared image rules."""

        return _validate_branding_image(value)


class OrganizationBrandingOutputSerializer(serializers.Serializer):
    """Output serializer for branding upload responses."""

    asset_url = serializers.URLField(read_only=True)
    message = serializers.CharField(read_only=True)


def _build_media_url(request, file_field) -> str | None:
    """Build an absolute media URL when a file exists."""

    if not file_field:
        return None

    if request is None:
        return file_field.url

    return request.build_absolute_uri(file_field.url)


def _validate_branding_image(value: Any) -> Any:
    """Normalize service-level image errors to serializer field errors."""

    try:
        return validate_organization_image(uploaded_file=value)
    except DRFValidationError as exc:
        detail = exc.detail
        if isinstance(detail, dict) and "file" in detail:
            messages = detail["file"]
            if isinstance(messages, list):
                raise serializers.ValidationError([str(message) for message in messages]) from exc
            raise serializers.ValidationError([str(messages)]) from exc

        raise serializers.ValidationError([str(detail)]) from exc
