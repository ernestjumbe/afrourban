"""Serializers for event API input and output."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError

from events.models import Event, EventCategory, EventLocationType
from events.services import (
    ORGANIZER_CONTEXT_IMMUTABLE_ERROR,
    validate_event_cover_image,
)


class EventLocationInputSerializer(serializers.Serializer):
    """Nested input serializer for event location payloads."""

    type = serializers.ChoiceField(
        choices=EventLocationType.choices,
        help_text="Whether the event uses a physical or web location.",
    )
    web_url = serializers.URLField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Web address for online events.",
    )
    country = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        trim_whitespace=True,
        help_text="Country for physical event locations.",
    )
    state = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        trim_whitespace=True,
        help_text="State or region for physical event locations.",
    )
    city = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        trim_whitespace=True,
        help_text="City or town for physical event locations.",
    )
    postcode = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        trim_whitespace=True,
        help_text="Postcode or zipcode for physical event locations.",
    )


class EventCreateInputSerializer(serializers.Serializer):
    """Input serializer for personal and organization-owned event creates."""

    title = serializers.CharField(
        max_length=Event.TITLE_MAX_LENGTH,
        trim_whitespace=True,
        help_text="Public event title.",
    )
    description = serializers.CharField(
        max_length=Event.DESCRIPTION_MAX_LENGTH,
        trim_whitespace=True,
        help_text="Public event description.",
    )
    category = serializers.ChoiceField(
        choices=EventCategory.choices,
        required=False,
        default=EventCategory.OTHER,
        help_text="Primary event category. Defaults to other.",
    )
    organization_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        help_text="Optional organization to create the event under.",
    )
    start_at = serializers.DateTimeField(
        help_text="Scheduled event start date and time.",
    )
    end_at = serializers.DateTimeField(
        help_text="Scheduled event end date and time.",
    )
    location = EventLocationInputSerializer(
        help_text="Structured event location payload.",
    )
    tickets_url = serializers.URLField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Optional tickets or registration link.",
    )


class EventUpdateInputSerializer(serializers.Serializer):
    """Input serializer for event patch requests."""

    title = serializers.CharField(
        max_length=Event.TITLE_MAX_LENGTH,
        required=False,
        trim_whitespace=True,
        help_text="Updated public event title.",
    )
    description = serializers.CharField(
        max_length=Event.DESCRIPTION_MAX_LENGTH,
        required=False,
        trim_whitespace=True,
        help_text="Updated public event description.",
    )
    category = serializers.ChoiceField(
        choices=EventCategory.choices,
        required=False,
        help_text="Updated primary event category.",
    )
    start_at = serializers.DateTimeField(
        required=False,
        help_text="Updated event start date and time.",
    )
    end_at = serializers.DateTimeField(
        required=False,
        help_text="Updated event end date and time.",
    )
    location = EventLocationInputSerializer(
        required=False,
        help_text="Updated structured event location payload.",
    )
    tickets_url = serializers.URLField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Updated tickets or registration link.",
    )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Reject attempts to mutate the organizer context."""

        if "organization_id" in self.initial_data:
            raise serializers.ValidationError(
                {
                    "organization_id": [ORGANIZER_CONTEXT_IMMUTABLE_ERROR],
                }
            )

        if "owner_user_id" in self.initial_data:
            raise serializers.ValidationError(
                {
                    "owner_user_id": [ORGANIZER_CONTEXT_IMMUTABLE_ERROR],
                }
            )

        return attrs


class EventDetailSerializer(serializers.Serializer):
    """Output serializer for event detail and create responses."""

    id = serializers.IntegerField(read_only=True)
    organizer_type = serializers.CharField(read_only=True)
    owner_user_id = serializers.IntegerField(
        source="owner_id",
        read_only=True,
        allow_null=True,
    )
    organization_id = serializers.IntegerField(read_only=True, allow_null=True)
    title = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    category = serializers.CharField(read_only=True)
    start_at = serializers.DateTimeField(read_only=True)
    end_at = serializers.DateTimeField(read_only=True)
    location = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()
    tickets_url = serializers.URLField(read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def get_location(self, obj: Event) -> dict[str, str | None]:
        """Return the current event location in contract shape."""

        return {
            "type": obj.location_type,
            "web_url": obj.location_web_url,
            "country": obj.location_country,
            "state": obj.location_state,
            "city": obj.location_city,
            "postcode": obj.location_postcode,
        }

    def get_cover_image_url(self, obj: Event) -> str | None:
        """Return the absolute cover-image URL when available."""

        return _build_media_url(self.context.get("request"), obj.cover_image)


class EventCoverUploadSerializer(serializers.Serializer):
    """Input serializer for event cover-image uploads."""

    cover_image = serializers.FileField(
        required=True,
        help_text="Event cover image (JPEG, PNG, or WebP, max 5MB).",
    )

    def validate_cover_image(self, value: Any) -> Any:
        """Validate cover-image uploads against the shared image rules."""

        return _validate_cover_image(value)


class EventCoverOutputSerializer(serializers.Serializer):
    """Output serializer for successful event cover mutations."""

    asset_url = serializers.URLField(read_only=True)
    message = serializers.CharField(read_only=True)


def _build_media_url(request, file_field) -> str | None:
    """Build an absolute media URL when a file exists."""

    if not file_field:
        return None

    if request is None:
        return file_field.url

    return request.build_absolute_uri(file_field.url)


def _validate_cover_image(value: Any) -> Any:
    """Normalize service-level image errors to serializer field errors."""

    try:
        return validate_event_cover_image(uploaded_file=value)
    except DRFValidationError as exc:
        detail = exc.detail
        if isinstance(detail, dict) and "file" in detail:
            messages = detail["file"]
            if isinstance(messages, list):
                raise serializers.ValidationError([str(message) for message in messages]) from exc
            raise serializers.ValidationError([str(messages)]) from exc

        raise serializers.ValidationError([str(detail)]) from exc
