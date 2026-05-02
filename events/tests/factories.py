"""Test factories and helpers for events."""

from __future__ import annotations

import base64
from datetime import timedelta

import factory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from events.models import Event
from organizations.tests.factories import OrganizationFactory
from users.tests.factories import UserFactory

_PNG_1X1_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+c4Z8AAAAASUVORK5CYII="
)


class EventFactory(factory.django.DjangoModelFactory):
    """Factory for creating personal Event instances in tests."""

    class Meta:
        model = Event

    owner = factory.SubFactory(UserFactory)
    organization = None
    title = factory.Sequence(lambda n: f"Event {n}")
    description = factory.Faker("text", max_nb_chars=200)
    category = "other"
    start_at = factory.LazyFunction(timezone.now)
    end_at = factory.LazyAttribute(lambda obj: obj.start_at + timedelta(hours=2))
    location_type = "physical"
    location_web_url = None
    location_country = "Denmark"
    location_state = "Capital Region"
    location_city = "Copenhagen"
    location_postcode = "2100"
    cover_image = None
    tickets_url = None


class OrganizationEventFactory(factory.django.DjangoModelFactory):
    """Factory for creating organization-owned Event instances in tests."""

    class Meta:
        model = Event

    owner = None
    organization = factory.SubFactory(OrganizationFactory)
    title = factory.Sequence(lambda n: f"Organization Event {n}")
    description = factory.Faker("text", max_nb_chars=200)
    category = "other"
    start_at = factory.LazyFunction(timezone.now)
    end_at = factory.LazyAttribute(lambda obj: obj.start_at + timedelta(hours=2))
    location_type = "physical"
    location_web_url = None
    location_country = "Denmark"
    location_state = "Capital Region"
    location_city = "Copenhagen"
    location_postcode = "2100"
    cover_image = None
    tickets_url = None


def personal_event_payload(
    *,
    title: str = "Community Dance Night",
    description: str = "An evening event for community dancers.",
    category: str | None = "other",
    start_at: str = "2026-05-01T18:00:00Z",
    end_at: str = "2026-05-01T21:00:00Z",
    location: dict[str, str] | None = None,
    tickets_url: str | None = None,
) -> dict[str, object]:
    """Build a personal-event create payload for tests."""

    payload: dict[str, object] = {
        "title": title,
        "description": description,
        "start_at": start_at,
        "end_at": end_at,
        "location": location
        or {
            "type": "physical",
            "country": "Denmark",
            "state": "Capital Region",
            "city": "Copenhagen",
            "postcode": "2100",
        },
        "tickets_url": tickets_url,
    }
    if category is not None:
        payload["category"] = category
    return payload


def organization_event_payload(
    *,
    organization_id: int = 1,
    title: str = "Organization Launch Party",
    description: str = "Celebrate a new organization event.",
    category: str | None = "other",
    start_at: str = "2026-05-02T18:00:00Z",
    end_at: str = "2026-05-02T22:00:00Z",
    location: dict[str, str] | None = None,
    tickets_url: str | None = None,
) -> dict[str, object]:
    """Build an organization-event create payload for tests."""

    payload = personal_event_payload(
        title=title,
        description=description,
        category=category,
        start_at=start_at,
        end_at=end_at,
        location=location,
        tickets_url=tickets_url,
    )
    payload["organization_id"] = organization_id
    return payload


def event_update_payload(
    *,
    title: str = "Updated Event Title",
    description: str = "Updated event description.",
    category: str = "community",
    start_at: str = "2026-05-03T18:00:00Z",
    end_at: str = "2026-05-03T21:00:00Z",
    location: dict[str, str] | None = None,
    tickets_url: str | None = "https://example.com/tickets",
) -> dict[str, object]:
    """Build an event update payload for tests."""

    return {
        "title": title,
        "description": description,
        "category": category,
        "start_at": start_at,
        "end_at": end_at,
        "location": location
        or {
            "type": "web",
            "web_url": "https://example.com/live",
        },
        "tickets_url": tickets_url,
    }


def event_uploaded_image(
    *,
    name: str = "event-cover.png",
    content_type: str = "image/png",
) -> SimpleUploadedFile:
    """Create a minimal valid uploaded cover image for tests."""

    return SimpleUploadedFile(
        name=name,
        content=_PNG_1X1_BYTES,
        content_type=content_type,
    )
