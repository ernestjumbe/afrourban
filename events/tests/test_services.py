"""Service tests for events."""

from __future__ import annotations

import json
from datetime import datetime

import pytest
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from events.models import EventAuditEntry, EventAuditField, EventCategory, EventLocationType
from events.services import event_create, event_update
from events.tests.factories import EventFactory, OrganizationEventFactory
from organizations.tests.factories import OrganizationFactory
from users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_event_create_persists_personal_owner_and_normalized_fields():
    """Personal event creation should assign the owner and normalize fields."""

    owner = UserFactory()

    event = event_create(
        owner=owner,
        title="  Community Dance Night  ",
        description="  A neighborhood dance gathering.  ",
        category=EventCategory.COMMUNITY,
        start_at=_aware_datetime(2026, 5, 1, 18, 0),
        end_at=_aware_datetime(2026, 5, 1, 21, 0),
        location={
            "type": "physical",
            "country": "  Denmark ",
            "state": " Capital Region ",
            "city": " Copenhagen ",
            "postcode": " 2100 ",
        },
        tickets_url="  https://example.com/tickets  ",
    )

    assert event.pk is not None
    assert event.owner_id == owner.pk
    assert event.organization_id is None
    assert event.title == "Community Dance Night"
    assert event.description == "A neighborhood dance gathering."
    assert event.category == EventCategory.COMMUNITY
    assert event.location_type == EventLocationType.PHYSICAL
    assert event.location_web_url is None
    assert event.location_country == "Denmark"
    assert event.location_state == "Capital Region"
    assert event.location_city == "Copenhagen"
    assert event.location_postcode == "2100"
    assert event.tickets_url == "https://example.com/tickets"


def test_event_create_defaults_category_to_other_and_accepts_web_location():
    """Personal event creation should default the category and persist web mode."""

    owner = UserFactory()

    event = event_create(
        owner=owner,
        title="Digital Watch Party",
        description="A live stream for the community.",
        category=None,
        start_at=_aware_datetime(2026, 5, 2, 19, 0),
        end_at=_aware_datetime(2026, 5, 2, 22, 0),
        location={
            "type": "web",
            "web_url": " https://example.com/live ",
        },
        tickets_url=None,
    )

    assert event.category == EventCategory.OTHER
    assert event.location_type == EventLocationType.WEB
    assert event.location_web_url == "https://example.com/live"
    assert event.location_country is None
    assert event.location_state is None
    assert event.location_city is None
    assert event.location_postcode is None


def test_event_create_rejects_end_at_not_later_than_start_at():
    """Event creation should reject invalid schedule ordering."""

    owner = UserFactory()

    with pytest.raises(ValidationError) as exc_info:
        event_create(
            owner=owner,
            title="Backwards Schedule",
            description="This should fail.",
            category=EventCategory.OTHER,
            start_at=_aware_datetime(2026, 5, 3, 20, 0),
            end_at=_aware_datetime(2026, 5, 3, 20, 0),
            location={
                "type": "web",
                "web_url": "https://example.com/live",
            },
            tickets_url=None,
        )

    assert exc_info.value.detail == {
        "end_at": ["End date and time must be later than the start date and time."]
    }


def test_event_create_requires_complete_physical_location():
    """Physical personal events should require all address components."""

    owner = UserFactory()

    with pytest.raises(ValidationError) as exc_info:
        event_create(
            owner=owner,
            title="Incomplete Venue",
            description="Missing location information.",
            category=EventCategory.OTHER,
            start_at=_aware_datetime(2026, 5, 4, 18, 0),
            end_at=_aware_datetime(2026, 5, 4, 21, 0),
            location={
                "type": "physical",
                "country": "Denmark",
                "state": "",
                "city": "Copenhagen",
                "postcode": "",
            },
            tickets_url=None,
        )

    assert exc_info.value.detail == {
        "location_state": ["State is required for physical event locations."],
        "location_postcode": ["Postcode or zipcode is required for physical event locations."],
    }


def test_event_create_requires_web_url_for_web_location():
    """Web personal events should require a web address."""

    owner = UserFactory()

    with pytest.raises(ValidationError) as exc_info:
        event_create(
            owner=owner,
            title="Missing Stream URL",
            description="This should fail.",
            category=EventCategory.OTHER,
            start_at=_aware_datetime(2026, 5, 5, 18, 0),
            end_at=_aware_datetime(2026, 5, 5, 21, 0),
            location={"type": "web", "web_url": "   "},
            tickets_url=None,
        )

    assert exc_info.value.detail == {
        "location_web_url": ["Web address is required for web event locations."]
    }


def test_event_create_persists_owned_organization_context():
    """Organization owners should be able to create organization-owned events."""

    owner = UserFactory()
    organization = OrganizationFactory(owner=owner)

    event = event_create(
        owner=owner,
        organization_id=organization.pk,
        title="Organization Launch Party",
        description="Celebrate a new organization event.",
        category=EventCategory.BUSINESS_NETWORKING,
        start_at=_aware_datetime(2026, 5, 6, 18, 0),
        end_at=_aware_datetime(2026, 5, 6, 22, 0),
        location={"type": "web", "web_url": "https://example.com/live"},
        tickets_url=None,
    )

    assert event.pk is not None
    assert event.owner_id is None
    assert event.organization_id == organization.pk
    assert event.organizer_type == "organization"
    assert event.category == EventCategory.BUSINESS_NETWORKING


def test_event_create_rejects_non_owner_for_organization_event():
    """Non-owners should not be able to create organization-owned events."""

    owner = UserFactory()
    actor = UserFactory()
    organization = OrganizationFactory(owner=owner)

    with pytest.raises(PermissionDenied) as exc_info:
        event_create(
            owner=actor,
            organization_id=organization.pk,
            title="Unauthorized Organization Event",
            description="This should fail.",
            category=EventCategory.OTHER,
            start_at=_aware_datetime(2026, 5, 7, 18, 0),
            end_at=_aware_datetime(2026, 5, 7, 21, 0),
            location={"type": "web", "web_url": "https://example.com/live"},
            tickets_url=None,
        )

    assert str(exc_info.value.detail) == "You do not have permission to create an event for this organization."


def test_event_update_persists_requested_metadata_and_audits_tracked_fields():
    """Tracked fields should create audit rows while untracked fields should not."""

    owner = UserFactory()
    original_start = _aware_datetime(2026, 5, 8, 18, 0)
    original_end = _aware_datetime(2026, 5, 8, 21, 0)
    event = EventFactory(
        owner=owner,
        organization=None,
        title="Original Event Title",
        description="Original description.",
        category=EventCategory.COMMUNITY,
        start_at=original_start,
        end_at=original_end,
        location_type=EventLocationType.PHYSICAL,
        location_country="Denmark",
        location_state="Capital Region",
        location_city="Copenhagen",
        location_postcode="2100",
        tickets_url="https://example.com/original",
    )
    updated_start = _aware_datetime(2026, 5, 8, 19, 0)
    updated_end = _aware_datetime(2026, 5, 8, 22, 0)

    updated = event_update(
        event=event,
        actor=owner,
        title="  Updated Event Title  ",
        description="Updated description.",
        category=EventCategory.ARTS_CULTURE,
        start_at=updated_start,
        end_at=updated_end,
        tickets_url=None,
    )

    assert updated.title == "Updated Event Title"
    assert updated.description == "Updated description."
    assert updated.category == EventCategory.ARTS_CULTURE
    assert updated.start_at == updated_start
    assert updated.end_at == updated_end
    assert updated.tickets_url is None

    audits_by_field = {
        entry.field_name: entry
        for entry in EventAuditEntry.objects.filter(event=event)
    }

    assert set(audits_by_field) == {
        EventAuditField.TITLE,
        EventAuditField.START_AT,
        EventAuditField.END_AT,
    }
    assert audits_by_field[EventAuditField.TITLE].actor_id == owner.pk
    assert audits_by_field[EventAuditField.TITLE].old_value == "Original Event Title"
    assert audits_by_field[EventAuditField.TITLE].new_value == "Updated Event Title"
    assert audits_by_field[EventAuditField.START_AT].old_value == original_start.isoformat()
    assert audits_by_field[EventAuditField.START_AT].new_value == updated_start.isoformat()
    assert audits_by_field[EventAuditField.END_AT].old_value == original_end.isoformat()
    assert audits_by_field[EventAuditField.END_AT].new_value == updated_end.isoformat()


def test_event_update_switches_location_mode_and_audits_full_location_state():
    """Location transitions should clear inactive fields and record one audit row."""

    owner = UserFactory()
    event = EventFactory(
        owner=owner,
        organization=None,
        location_type=EventLocationType.WEB,
        location_web_url="https://example.com/original-live",
        location_country=None,
        location_state=None,
        location_city=None,
        location_postcode=None,
    )

    updated = event_update(
        event=event,
        actor=owner,
        location={
            "type": "physical",
            "country": "Denmark",
            "state": "Capital Region",
            "city": "Copenhagen",
            "postcode": "2100",
        },
    )

    assert updated.location_type == EventLocationType.PHYSICAL
    assert updated.location_web_url is None
    assert updated.location_country == "Denmark"
    assert updated.location_state == "Capital Region"
    assert updated.location_city == "Copenhagen"
    assert updated.location_postcode == "2100"

    audit_entry = EventAuditEntry.objects.get(
        event=event,
        field_name=EventAuditField.LOCATION,
    )
    assert audit_entry.actor_id == owner.pk
    assert json.loads(audit_entry.old_value) == {
        "type": "web",
        "web_url": "https://example.com/original-live",
        "country": None,
        "state": None,
        "city": None,
        "postcode": None,
    }
    assert json.loads(audit_entry.new_value) == {
        "type": "physical",
        "web_url": None,
        "country": "Denmark",
        "state": "Capital Region",
        "city": "Copenhagen",
        "postcode": "2100",
    }


def test_event_update_rejects_organizer_context_changes():
    """Organizer ownership context should remain immutable after creation."""

    owner = UserFactory()
    organization = OrganizationFactory(owner=owner)
    event = EventFactory(owner=owner, organization=None)

    with pytest.raises(ValidationError) as exc_info:
        event_update(
            event=event,
            actor=owner,
            organization_id=organization.pk,
        )

    assert exc_info.value.detail == {
        "organization_id": ["Organizer context cannot be changed after creation."]
    }


def test_event_update_rejects_non_owner_for_organization_event():
    """Only the effective organization owner should be able to update the event."""

    owner = UserFactory()
    actor = UserFactory()
    organization = OrganizationFactory(owner=owner)
    event = OrganizationEventFactory(organization=organization, owner=None)

    with pytest.raises(PermissionDenied) as exc_info:
        event_update(
            event=event,
            actor=actor,
            title="Unauthorized Update",
        )

    assert str(exc_info.value.detail) == "You do not have permission to modify this event."


def _aware_datetime(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
) -> datetime:
    """Build a timezone-aware datetime for tests."""

    return timezone.make_aware(datetime(year, month, day, hour, minute))
