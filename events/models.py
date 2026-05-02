"""Models for event entities."""

from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from organizations.models import Organization


def _normalize_optional_text(value: str | None) -> str | None:
    """Trim optional string values and collapse blanks to ``None``."""

    if value is None:
        return None

    normalized_value = value.strip()
    return normalized_value or None


class EventCategory(models.TextChoices):
    """Supported event classifications."""

    MUSIC = "music", "Music"
    FOOD_DRINK = "food_drink", "Food & Drink"
    ARTS_CULTURE = "arts_culture", "Arts & Culture"
    COMMUNITY = "community", "Community"
    SPORTS_FITNESS = "sports_fitness", "Sports & Fitness"
    BUSINESS_NETWORKING = "business_networking", "Business & Networking"
    EDUCATION_WORKSHOP = "education_workshop", "Education & Workshop"
    OTHER = "other", "Other"


class EventLocationType(models.TextChoices):
    """Supported event location modes."""

    PHYSICAL = "physical", "Physical"
    WEB = "web", "Web"


class EventAuditField(models.TextChoices):
    """Tracked event fields for immutable audit entries."""

    TITLE = "title", "Title"
    START_AT = "start_at", "Start Time"
    END_AT = "end_at", "End Time"
    LOCATION = "location", "Location"


class Event(models.Model):
    """Scheduled activity owned by a user or an organization."""

    TITLE_MAX_LENGTH = 255
    DESCRIPTION_MAX_LENGTH = 1000
    CATEGORY_MAX_LENGTH = 32
    LOCATION_TYPE_MAX_LENGTH = 16
    URL_MAX_LENGTH = 500
    COUNTRY_MAX_LENGTH = 100
    STATE_MAX_LENGTH = 100
    CITY_MAX_LENGTH = 100
    POSTCODE_MAX_LENGTH = 32

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="personal_events",
        blank=True,
        null=True,
        help_text="User who owns this personal event.",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="events",
        blank=True,
        null=True,
        help_text="Organization that owns this event when not personal.",
    )
    title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        help_text="Public event title.",
    )
    description = models.TextField(
        max_length=DESCRIPTION_MAX_LENGTH,
        help_text="Public event description.",
    )
    category = models.CharField(
        max_length=CATEGORY_MAX_LENGTH,
        choices=EventCategory.choices,
        default=EventCategory.OTHER,
        help_text="Primary event category.",
    )
    start_at = models.DateTimeField(
        help_text="Scheduled event start date and time.",
    )
    end_at = models.DateTimeField(
        help_text="Scheduled event end date and time.",
    )
    location_type = models.CharField(
        max_length=LOCATION_TYPE_MAX_LENGTH,
        choices=EventLocationType.choices,
        help_text="Whether the event uses a physical or web location.",
    )
    location_web_url = models.URLField(
        max_length=URL_MAX_LENGTH,
        blank=True,
        null=True,
        help_text="Web address for online events.",
    )
    location_country = models.CharField(
        max_length=COUNTRY_MAX_LENGTH,
        blank=True,
        null=True,
        help_text="Country for physical event locations.",
    )
    location_state = models.CharField(
        max_length=STATE_MAX_LENGTH,
        blank=True,
        null=True,
        help_text="State or region for physical event locations.",
    )
    location_city = models.CharField(
        max_length=CITY_MAX_LENGTH,
        blank=True,
        null=True,
        help_text="City or town for physical event locations.",
    )
    location_postcode = models.CharField(
        max_length=POSTCODE_MAX_LENGTH,
        blank=True,
        null=True,
        help_text="Postcode or zipcode for physical event locations.",
    )
    cover_image = models.ImageField(
        upload_to="events/covers/",
        blank=True,
        null=True,
        help_text="Optional event cover image.",
    )
    tickets_url = models.URLField(
        max_length=URL_MAX_LENGTH,
        blank=True,
        null=True,
        help_text="Optional tickets or registration link.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "event"
        verbose_name_plural = "events"
        ordering = ["-created_at", "title"]
        indexes = [
            models.Index(fields=["owner", "-created_at"]),
            models.Index(fields=["organization", "-created_at"]),
            models.Index(fields=["category", "start_at"]),
            models.Index(fields=["location_type", "start_at"]),
            models.Index(fields=["created_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(owner__isnull=False, organization__isnull=True)
                    | models.Q(owner__isnull=True, organization__isnull=False)
                ),
                name="events_event_exactly_one_owner",
            ),
            models.CheckConstraint(
                condition=models.Q(end_at__gt=models.F("start_at")),
                name="events_event_end_after_start",
            ),
        ]

    def __str__(self) -> str:
        """Return the public event title."""

        return self.title

    @property
    def organizer_type(self) -> str:
        """Return the organizer context label for the event."""

        return "organization" if self.organization_id is not None else "person"

    def clean(self) -> None:
        """Enforce core organizer, schedule, and location constraints."""

        super().clean()

        self.title = (self.title or "").strip()
        self.description = (self.description or "").strip()
        self.location_web_url = _normalize_optional_text(self.location_web_url)
        self.location_country = _normalize_optional_text(self.location_country)
        self.location_state = _normalize_optional_text(self.location_state)
        self.location_city = _normalize_optional_text(self.location_city)
        self.location_postcode = _normalize_optional_text(self.location_postcode)
        self.tickets_url = _normalize_optional_text(self.tickets_url)

        errors: dict[str, list[str]] = {}

        has_owner = self.owner_id is not None
        has_organization = self.organization_id is not None
        if has_owner == has_organization:
            errors["owner"] = [
                "Exactly one organizer context must be set on an event."
            ]

        if self.end_at and self.start_at and self.end_at <= self.start_at:
            errors["end_at"] = [
                "End date and time must be later than the start date and time."
            ]

        if self.location_type == EventLocationType.WEB:
            self.location_country = None
            self.location_state = None
            self.location_city = None
            self.location_postcode = None
            if self.location_web_url is None:
                errors["location_web_url"] = [
                    "Web address is required for web event locations."
                ]
        elif self.location_type == EventLocationType.PHYSICAL:
            self.location_web_url = None

            required_physical_fields = (
                ("location_country", self.location_country, "Country is required."),
                ("location_state", self.location_state, "State is required."),
                ("location_city", self.location_city, "City or town is required."),
                (
                    "location_postcode",
                    self.location_postcode,
                    "Postcode or zipcode is required.",
                ),
            )
            for field_name, value, message in required_physical_fields:
                if value is None:
                    errors[field_name] = [message]

        if errors:
            raise ValidationError(errors)


class EventAuditEntry(models.Model):
    """Immutable audit record for tracked event-field changes."""

    FIELD_NAME_MAX_LENGTH = 16

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="audit_entries",
        help_text="Event whose tracked field changed.",
    )
    field_name = models.CharField(
        max_length=FIELD_NAME_MAX_LENGTH,
        choices=EventAuditField.choices,
        help_text="Tracked event field that changed.",
    )
    old_value = models.TextField(
        help_text="Previous normalized value for the tracked field.",
    )
    new_value = models.TextField(
        help_text="New normalized value for the tracked field.",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_audit_entries",
        help_text="User who made the tracked event change.",
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "event audit entry"
        verbose_name_plural = "event audit entries"
        ordering = ["-changed_at", "-id"]
        indexes = [
            models.Index(fields=["event", "-changed_at"]),
            models.Index(fields=["actor", "-changed_at"]),
            models.Index(fields=["field_name", "-changed_at"]),
        ]

    def __str__(self) -> str:
        """Return a compact audit entry summary."""

        return f"EventAuditEntry(event={self.event_id}, field={self.field_name})"
