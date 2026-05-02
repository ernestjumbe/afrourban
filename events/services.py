"""Services for event write operations."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Iterable, Mapping, cast

import structlog
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from events.models import (
    Event,
    EventAuditEntry,
    EventAuditField,
    EventCategory,
    EventLocationType,
)
from events.permissions import can_write_event
from organizations.models import Organization
from organizations.permissions import is_organization_owner
from organizations.selectors import organization_get_by_id

if TYPE_CHECKING:
    from organizations.models import Organization as OrganizationModel
    from users.models import CustomUser

logger = structlog.get_logger(__name__)

_UNSET = object()
ALLOWED_IMAGE_CONTENT_TYPES = ("image/jpeg", "image/png", "image/webp")
MAX_IMAGE_FILE_SIZE = 5 * 1024 * 1024
END_BEFORE_START_ERROR = "End date and time must be later than the start date and time."
WEB_LOCATION_REQUIRED_ERROR = "Web address is required for web event locations."
INVALID_LOCATION_TYPE_ERROR = "Location type must be either physical or web."
ORGANIZATION_CREATE_PERMISSION_ERROR = (
    "You do not have permission to create an event for this organization."
)
EVENT_WRITE_PERMISSION_ERROR = "You do not have permission to modify this event."
ORGANIZATION_NOT_FOUND_ERROR = "Organization does not exist."
ORGANIZER_CONTEXT_IMMUTABLE_ERROR = (
    "Organizer context cannot be changed after creation."
)
PHYSICAL_LOCATION_REQUIRED_ERRORS = {
    "location_country": "Country is required for physical event locations.",
    "location_state": "State is required for physical event locations.",
    "location_city": "City or town is required for physical event locations.",
    "location_postcode": "Postcode or zipcode is required for physical event locations.",
}


def normalize_event_title(*, title: str) -> str:
    """Normalize event title input before validation or persistence."""

    return title.strip()


def normalize_event_description(*, description: str) -> str:
    """Normalize event description input before validation or persistence."""

    return description.strip()


def normalize_optional_text(*, value: str | None) -> str | None:
    """Normalize optional text values and collapse blanks to ``None``."""

    if value is None:
        return None

    normalized_value = value.strip()
    return normalized_value or None


def normalize_location_type(*, location_type: str) -> str:
    """Normalize location-type input."""

    return location_type.strip().lower()


def validate_event_schedule(
    *,
    start_at: datetime,
    end_at: datetime,
) -> None:
    """Validate the event schedule ordering."""

    if end_at <= start_at:
        raise ValidationError({"end_at": [END_BEFORE_START_ERROR]})


def validate_event_location(
    *,
    location_type: str,
    location_web_url: str | None,
    location_country: str | None,
    location_state: str | None,
    location_city: str | None,
    location_postcode: str | None,
) -> dict[str, str | None]:
    """Validate and normalize the mutually exclusive event location payload."""

    normalized_location_type = normalize_location_type(location_type=location_type)
    normalized_web_url = normalize_optional_text(value=location_web_url)
    normalized_country = normalize_optional_text(value=location_country)
    normalized_state = normalize_optional_text(value=location_state)
    normalized_city = normalize_optional_text(value=location_city)
    normalized_postcode = normalize_optional_text(value=location_postcode)

    if normalized_location_type == EventLocationType.WEB:
        if normalized_web_url is None:
            raise ValidationError({"location_web_url": [WEB_LOCATION_REQUIRED_ERROR]})

        return {
            "location_type": str(EventLocationType.WEB),
            "location_web_url": normalized_web_url,
            "location_country": None,
            "location_state": None,
            "location_city": None,
            "location_postcode": None,
        }

    if normalized_location_type == EventLocationType.PHYSICAL:
        errors = {
            field_name: [message]
            for field_name, value, message in (
                (
                    "location_country",
                    normalized_country,
                    PHYSICAL_LOCATION_REQUIRED_ERRORS["location_country"],
                ),
                (
                    "location_state",
                    normalized_state,
                    PHYSICAL_LOCATION_REQUIRED_ERRORS["location_state"],
                ),
                (
                    "location_city",
                    normalized_city,
                    PHYSICAL_LOCATION_REQUIRED_ERRORS["location_city"],
                ),
                (
                    "location_postcode",
                    normalized_postcode,
                    PHYSICAL_LOCATION_REQUIRED_ERRORS["location_postcode"],
                ),
            )
            if value is None
        }

        if errors:
            raise ValidationError(errors)

        return {
            "location_type": str(EventLocationType.PHYSICAL),
            "location_web_url": None,
            "location_country": normalized_country,
            "location_state": normalized_state,
            "location_city": normalized_city,
            "location_postcode": normalized_postcode,
        }

    raise ValidationError({"location_type": [INVALID_LOCATION_TYPE_ERROR]})


def serialize_location_for_audit(
    *,
    location_type: str,
    location_web_url: str | None,
    location_country: str | None,
    location_state: str | None,
    location_city: str | None,
    location_postcode: str | None,
) -> str:
    """Serialize the normalized event location state for audit persistence."""

    return json.dumps(
        {
            "type": location_type,
            "web_url": location_web_url,
            "country": location_country,
            "state": location_state,
            "city": location_city,
            "postcode": location_postcode,
        },
        sort_keys=True,
    )


def validate_event_cover_image(*, uploaded_file: UploadedFile) -> UploadedFile:
    """Validate image type and size for event cover assets."""

    if uploaded_file.size > MAX_IMAGE_FILE_SIZE:
        raise ValidationError({"file": ["File size exceeds 5MB limit."]})

    content_type = getattr(uploaded_file, "content_type", None)
    if content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise ValidationError(
            {"file": ["Unsupported file format. Use JPEG, PNG, or WebP."]}
        )

    return uploaded_file


def resolve_event_organizer(
    *,
    actor: "CustomUser",
    organization_id: int | None,
) -> tuple["CustomUser | None", "OrganizationModel | None"]:
    """Resolve and authorize the target organizer context for event creation."""

    if organization_id is None:
        return actor, None

    try:
        organization = organization_get_by_id(organization_id=organization_id)
    except Organization.DoesNotExist as exc:
        errors = {"organization_id": [ORGANIZATION_NOT_FOUND_ERROR]}
        log_event_outcome(
            outcome="create_validation_failed",
            actor_user_id=getattr(actor, "pk", None),
            organization_id=organization_id,
            reason="organization_not_found",
            details=errors,
        )
        raise ValidationError(errors) from exc

    if not is_organization_owner(user=actor, organization=organization):
        log_event_outcome(
            outcome="create_permission_denied",
            actor_user_id=getattr(actor, "pk", None),
            organization_id=organization.pk,
            reason="not_owner",
        )
        raise PermissionDenied(ORGANIZATION_CREATE_PERMISSION_ERROR)

    return None, organization


def event_create(
    *,
    owner: "CustomUser",
    organization_id: int | None = None,
    title: str,
    description: str,
    start_at: datetime,
    end_at: datetime,
    location: Mapping[str, str | None],
    category: str | None = None,
    tickets_url: str | None = None,
) -> Event:
    """Create a personal or organization-owned event for the authenticated user."""

    actor = owner
    normalized_title = normalize_event_title(title=title)
    normalized_description = normalize_event_description(description=description)
    normalized_tickets_url = normalize_optional_text(value=tickets_url)
    normalized_category = category or str(EventCategory.OTHER)
    event_owner, organization = resolve_event_organizer(
        actor=actor,
        organization_id=organization_id,
    )

    try:
        validate_event_schedule(start_at=start_at, end_at=end_at)
        normalized_location = validate_event_location(
            location_type=str(location.get("type", "")),
            location_web_url=location.get("web_url"),
            location_country=location.get("country"),
            location_state=location.get("state"),
            location_city=location.get("city"),
            location_postcode=location.get("postcode"),
        )
    except ValidationError:
        log_event_outcome(
            outcome="create_validation_failed",
            actor_user_id=getattr(actor, "pk", None),
            owner_user_id=getattr(event_owner, "pk", None),
            organization_id=getattr(organization, "pk", organization_id),
            reason="input_validation_failed",
        )
        raise

    event = Event(
        owner=event_owner,
        organization=organization,
        title=normalized_title,
        description=normalized_description,
        category=normalized_category,
        start_at=start_at,
        end_at=end_at,
        tickets_url=normalized_tickets_url,
        **normalized_location,
    )

    try:
        event.full_clean()
    except DjangoValidationError as exc:
        errors = coerce_django_validation_error(exc)
        log_event_outcome(
            outcome="create_validation_failed",
            actor_user_id=getattr(actor, "pk", None),
            owner_user_id=getattr(event_owner, "pk", None),
            organization_id=getattr(organization, "pk", organization_id),
            reason="model_validation_failed",
            details=errors,
        )
        raise ValidationError(errors) from exc

    with transaction.atomic():
        event.save()

    log_event_outcome(
        outcome="create_success",
        event_id=event.pk,
        actor_user_id=getattr(actor, "pk", None),
        owner_user_id=event.owner_id,
        organization_id=event.organization_id,
    )
    return event


def event_update(
    *,
    event: Event,
    actor: "CustomUser",
    title: str | object = _UNSET,
    description: str | object = _UNSET,
    category: str | object = _UNSET,
    start_at: datetime | object = _UNSET,
    end_at: datetime | object = _UNSET,
    location: Mapping[str, str | None] | object = _UNSET,
    tickets_url: str | None | object = _UNSET,
    organization_id: int | None | object = _UNSET,
) -> Event:
    """Update one event while preserving organizer immutability and audit rows."""

    _ensure_event_write_access(
        actor=actor,
        event=event,
        operation="update",
    )

    if organization_id is not _UNSET:
        errors = {
            "organization_id": [ORGANIZER_CONTEXT_IMMUTABLE_ERROR],
        }
        log_event_outcome(
            outcome="update_validation_failed",
            event_id=event.pk,
            actor_user_id=getattr(actor, "pk", None),
            owner_user_id=event.owner_id,
            organization_id=event.organization_id,
            reason="organizer_immutable",
            details=errors,
        )
        raise ValidationError(errors)

    normalized_title = event.title
    if title is not _UNSET:
        normalized_title = normalize_event_title(title=str(title))

    normalized_description = event.description
    if description is not _UNSET:
        normalized_description = normalize_event_description(description=str(description))

    normalized_category = event.category
    if category is not _UNSET:
        normalized_category = str(category)

    resulting_start_at = event.start_at if start_at is _UNSET else cast("datetime", start_at)
    resulting_end_at = event.end_at if end_at is _UNSET else cast("datetime", end_at)

    try:
        validate_event_schedule(
            start_at=resulting_start_at,
            end_at=resulting_end_at,
        )

        if location is _UNSET:
            normalized_location = {
                "location_type": event.location_type,
                "location_web_url": event.location_web_url,
                "location_country": event.location_country,
                "location_state": event.location_state,
                "location_city": event.location_city,
                "location_postcode": event.location_postcode,
            }
        else:
            location_data = cast("Mapping[str, str | None]", location)
            normalized_location = validate_event_location(
                location_type=str(location_data.get("type", "")),
                location_web_url=location_data.get("web_url"),
                location_country=location_data.get("country"),
                location_state=location_data.get("state"),
                location_city=location_data.get("city"),
                location_postcode=location_data.get("postcode"),
            )
    except ValidationError:
        log_event_outcome(
            outcome="update_validation_failed",
            event_id=event.pk,
            actor_user_id=getattr(actor, "pk", None),
            owner_user_id=event.owner_id,
            organization_id=event.organization_id,
            reason="input_validation_failed",
        )
        raise

    normalized_tickets_url = (
        event.tickets_url
        if tickets_url is _UNSET
        else normalize_optional_text(value=cast("str | None", tickets_url))
    )

    location_before = _serialize_event_location(event=event)
    location_after = serialize_location_for_audit(
        location_type=str(normalized_location["location_type"]),
        location_web_url=cast("str | None", normalized_location["location_web_url"]),
        location_country=cast("str | None", normalized_location["location_country"]),
        location_state=cast("str | None", normalized_location["location_state"]),
        location_city=cast("str | None", normalized_location["location_city"]),
        location_postcode=cast("str | None", normalized_location["location_postcode"]),
    )

    fields_to_update: list[str] = []
    audit_changes: list[dict[str, str]] = []

    if title is not _UNSET and event.title != normalized_title:
        audit_changes.append(
            {
                "field_name": str(EventAuditField.TITLE),
                "old_value": event.title,
                "new_value": normalized_title,
            }
        )
        event.title = normalized_title
        fields_to_update.append("title")

    if description is not _UNSET and event.description != normalized_description:
        event.description = normalized_description
        fields_to_update.append("description")

    if category is not _UNSET and event.category != normalized_category:
        event.category = normalized_category
        fields_to_update.append("category")

    if start_at is not _UNSET and event.start_at != resulting_start_at:
        audit_changes.append(
            {
                "field_name": str(EventAuditField.START_AT),
                "old_value": event.start_at.isoformat(),
                "new_value": resulting_start_at.isoformat(),
            }
        )
        event.start_at = resulting_start_at
        fields_to_update.append("start_at")

    if end_at is not _UNSET and event.end_at != resulting_end_at:
        audit_changes.append(
            {
                "field_name": str(EventAuditField.END_AT),
                "old_value": event.end_at.isoformat(),
                "new_value": resulting_end_at.isoformat(),
            }
        )
        event.end_at = resulting_end_at
        fields_to_update.append("end_at")

    if location is not _UNSET:
        for field_name, value in normalized_location.items():
            if getattr(event, field_name) != value:
                setattr(event, field_name, value)
                fields_to_update.append(field_name)

        if location_before != location_after:
            audit_changes.append(
                {
                    "field_name": str(EventAuditField.LOCATION),
                    "old_value": location_before,
                    "new_value": location_after,
                }
            )

    if tickets_url is not _UNSET and event.tickets_url != normalized_tickets_url:
        event.tickets_url = normalized_tickets_url
        fields_to_update.append("tickets_url")

    try:
        event.full_clean()
    except DjangoValidationError as exc:
        errors = coerce_django_validation_error(exc)
        log_event_outcome(
            outcome="update_validation_failed",
            event_id=event.pk,
            actor_user_id=getattr(actor, "pk", None),
            owner_user_id=event.owner_id,
            organization_id=event.organization_id,
            reason="model_validation_failed",
            details=errors,
        )
        raise ValidationError(errors) from exc

    unique_fields_to_update = list(dict.fromkeys(fields_to_update))
    if unique_fields_to_update:
        unique_fields_to_update.append("updated_at")

        with transaction.atomic():
            event.save(update_fields=unique_fields_to_update)
            create_event_audit_entries(
                event=event,
                actor=actor,
                changes=audit_changes,
            )

    log_event_outcome(
        outcome="update_success",
        event_id=event.pk,
        actor_user_id=getattr(actor, "pk", None),
        owner_user_id=event.owner_id,
        organization_id=event.organization_id,
        audit_entry_count=len(audit_changes),
    )
    return event


def event_cover_upload(
    *,
    event: Event,
    actor: "CustomUser",
    uploaded_file: UploadedFile,
) -> str:
    """Upload or replace one event cover image."""

    _ensure_event_write_access(
        actor=actor,
        event=event,
        operation="cover_upload",
    )

    try:
        validated_file = validate_event_cover_image(uploaded_file=uploaded_file)
    except ValidationError:
        log_event_outcome(
            outcome="cover_upload_validation_failed",
            event_id=event.pk,
            actor_user_id=getattr(actor, "pk", None),
            owner_user_id=event.owner_id,
            organization_id=event.organization_id,
            reason="invalid_file",
        )
        raise

    existing_file = event.cover_image
    if existing_file:
        existing_file.delete(save=False)

    generated_name = _generate_event_asset_filename(
        original_name=validated_file.name,
        event_id=event.pk,
        asset_kind="cover",
    )
    event.cover_image.save(generated_name, validated_file, save=False)
    event.save(update_fields=["cover_image", "updated_at"])

    log_event_outcome(
        outcome="cover_upload_success",
        event_id=event.pk,
        actor_user_id=getattr(actor, "pk", None),
        owner_user_id=event.owner_id,
        organization_id=event.organization_id,
    )
    return event.cover_image.url


def event_cover_delete(
    *,
    event: Event,
    actor: "CustomUser",
) -> None:
    """Delete an event cover image as a safe no-op when it is missing."""

    _ensure_event_write_access(
        actor=actor,
        event=event,
        operation="cover_delete",
    )

    existing_file = event.cover_image
    if not existing_file:
        log_event_outcome(
            outcome="cover_delete_noop",
            event_id=event.pk,
            actor_user_id=getattr(actor, "pk", None),
            owner_user_id=event.owner_id,
            organization_id=event.organization_id,
        )
        return

    existing_file.delete(save=False)
    event.cover_image = None
    event.save(update_fields=["cover_image", "updated_at"])

    log_event_outcome(
        outcome="cover_delete_success",
        event_id=event.pk,
        actor_user_id=getattr(actor, "pk", None),
        owner_user_id=event.owner_id,
        organization_id=event.organization_id,
    )


def create_event_audit_entries(
    *,
    event: Event,
    actor: "CustomUser",
    changes: Iterable[Mapping[str, str]],
) -> list[EventAuditEntry]:
    """Persist immutable audit entries for tracked event-field changes."""

    audit_entries = [
        EventAuditEntry(
            event=event,
            actor=actor,
            field_name=change["field_name"],
            old_value=change["old_value"],
            new_value=change["new_value"],
        )
        for change in changes
    ]

    if not audit_entries:
        return []

    with transaction.atomic():
        created_entries = EventAuditEntry.objects.bulk_create(audit_entries)

    log_event_outcome(
        outcome="audit_entries_created",
        event_id=event.pk,
        actor_user_id=getattr(actor, "pk", None),
        audit_entry_count=len(created_entries),
    )
    return created_entries


def coerce_django_validation_error(
    exc: DjangoValidationError,
) -> dict[str, list[str]]:
    """Convert Django ``ValidationError`` objects into REST-friendly payloads."""

    if hasattr(exc, "message_dict"):
        return {
            field_name: [str(message) for message in messages]
            for field_name, messages in exc.message_dict.items()
        }

    return {"non_field_errors": [str(message) for message in exc.messages]}


def log_event_outcome(
    *,
    outcome: str,
    event_id: int | None = None,
    actor_user_id: int | None = None,
    owner_user_id: int | None = None,
    organization_id: int | None = None,
    field_name: str | None = None,
    reason: str | None = None,
    audit_entry_count: int | None = None,
    details: Any | None = None,
) -> None:
    """Log structured event-domain outcomes for later service operations."""

    logger.info(
        "event_service_outcome",
        outcome=outcome,
        event_id=event_id,
        actor_user_id=actor_user_id,
        owner_user_id=owner_user_id,
        organization_id=organization_id,
        field_name=field_name,
        reason=reason,
        audit_entry_count=audit_entry_count,
        details=details,
    )


def _serialize_event_location(*, event: Event) -> str:
    """Serialize the current event location into the audit representation."""

    return serialize_location_for_audit(
        location_type=event.location_type,
        location_web_url=event.location_web_url,
        location_country=event.location_country,
        location_state=event.location_state,
        location_city=event.location_city,
        location_postcode=event.location_postcode,
    )


def _ensure_event_write_access(
    *,
    actor: "CustomUser",
    event: Event,
    operation: str,
) -> None:
    """Raise when the actor is not allowed to mutate the event."""

    if can_write_event(user=actor, event=event):
        return

    log_event_outcome(
        outcome=f"{operation}_permission_denied",
        event_id=event.pk,
        actor_user_id=getattr(actor, "pk", None),
        owner_user_id=event.owner_id,
        organization_id=event.organization_id,
        reason="not_owner",
    )
    raise PermissionDenied(EVENT_WRITE_PERMISSION_ERROR)


def _generate_event_asset_filename(
    *,
    original_name: str,
    event_id: int,
    asset_kind: str,
) -> str:
    """Generate a predictable-unique filename for event assets."""

    ext = os.path.splitext(original_name)[1].lower()
    unique_id = uuid.uuid4().hex[:8]
    return f"{event_id}_{asset_kind}_{unique_id}{ext}"
