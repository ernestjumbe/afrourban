"""Detail API tests for events."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from events.models import EventAuditEntry, EventAuditField, EventCategory, EventLocationType
from events.tests.factories import EventFactory, OrganizationEventFactory
from organizations.tests.factories import OrganizationFactory
from users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_authenticated_viewer_can_get_event_detail():
    """Any authenticated user should be able to view event details in v1."""

    owner = UserFactory()
    viewer = UserFactory()
    event = EventFactory(
        owner=owner,
        organization=None,
        title="Community Dance Night",
        description="A neighborhood dance gathering.",
        category=EventCategory.COMMUNITY,
        location_type=EventLocationType.PHYSICAL,
        location_country="Denmark",
        location_state="Capital Region",
        location_city="Copenhagen",
        location_postcode="2100",
        tickets_url="https://example.com/tickets",
    )

    client = APIClient()
    client.force_authenticate(user=viewer)

    response = client.get(f"/api/v1/events/{event.pk}/")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == event.pk
    assert data["organizer_type"] == "person"
    assert data["owner_user_id"] == owner.pk
    assert data["organization_id"] is None
    assert data["title"] == "Community Dance Night"
    assert data["description"] == "A neighborhood dance gathering."
    assert data["category"] == EventCategory.COMMUNITY
    assert data["location"] == {
        "type": "physical",
        "web_url": None,
        "country": "Denmark",
        "state": "Capital Region",
        "city": "Copenhagen",
        "postcode": "2100",
    }
    assert data["cover_image_url"] is None
    assert data["tickets_url"] == "https://example.com/tickets"


def test_owner_can_patch_event_metadata_and_create_audit_entries():
    """Patch should update event metadata and audit only tracked field changes."""

    owner = UserFactory()
    event = EventFactory(
        owner=owner,
        organization=None,
        title="Original Event Title",
        description="Original description.",
        category=EventCategory.COMMUNITY,
        location_type=EventLocationType.PHYSICAL,
        location_country="Denmark",
        location_state="Capital Region",
        location_city="Copenhagen",
        location_postcode="2100",
        tickets_url="https://example.com/original",
    )
    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.patch(
        f"/api/v1/events/{event.pk}/",
        {
            "title": "Updated Event Title",
            "description": "Updated description.",
            "category": EventCategory.ARTS_CULTURE,
            "start_at": "2026-05-03T19:00:00Z",
            "end_at": "2026-05-03T22:00:00Z",
            "location": {
                "type": "web",
                "web_url": "https://example.com/live",
            },
            "tickets_url": None,
        },
        format="json",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Event Title"
    assert data["description"] == "Updated description."
    assert data["category"] == EventCategory.ARTS_CULTURE
    assert data["start_at"] == "2026-05-03T19:00:00Z"
    assert data["end_at"] == "2026-05-03T22:00:00Z"
    assert data["location"] == {
        "type": "web",
        "web_url": "https://example.com/live",
        "country": None,
        "state": None,
        "city": None,
        "postcode": None,
    }
    assert data["tickets_url"] is None

    audit_fields = {
        entry.field_name
        for entry in EventAuditEntry.objects.filter(event=event)
    }
    assert audit_fields == {
        EventAuditField.TITLE,
        EventAuditField.START_AT,
        EventAuditField.END_AT,
        EventAuditField.LOCATION,
    }


def test_patch_event_rejects_organizer_context_change():
    """Patch requests must reject organizer reassignment attempts."""

    owner = UserFactory()
    organization = OrganizationFactory(owner=owner)
    event = EventFactory(owner=owner, organization=None)
    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.patch(
        f"/api/v1/events/{event.pk}/",
        {"organization_id": organization.pk},
        format="json",
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Validation failed"
    assert data["errors"] == {
        "organization_id": ["Organizer context cannot be changed after creation."]
    }


def test_non_owner_patch_returns_403_for_organization_event():
    """Non-owners should not be able to patch organization-owned events."""

    owner = UserFactory()
    viewer = UserFactory()
    organization = OrganizationFactory(owner=owner)
    event = OrganizationEventFactory(organization=organization, owner=None)
    client = APIClient()
    client.force_authenticate(user=viewer)

    response = client.patch(
        f"/api/v1/events/{event.pk}/",
        {"description": "Unauthorized update."},
        format="json",
    )

    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "You do not have permission to modify this event."
