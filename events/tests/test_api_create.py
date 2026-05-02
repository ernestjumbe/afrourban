"""Create API tests for events."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from events.tests.factories import organization_event_payload, personal_event_payload
from organizations.tests.factories import OrganizationFactory
from users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_create_personal_event_returns_201_and_assigns_authenticated_owner():
    """Authenticated users should be able to create personal physical events."""

    user = UserFactory()
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/v1/events/",
        personal_event_payload(
            title="Community Dance Night",
            description="A neighborhood dance gathering.",
            category="community",
        ),
        format="json",
    )

    assert response.status_code == 201
    data = response.json()
    assert data["organizer_type"] == "person"
    assert data["owner_user_id"] == user.pk
    assert data["organization_id"] is None
    assert data["title"] == "Community Dance Night"
    assert data["description"] == "A neighborhood dance gathering."
    assert data["category"] == "community"
    assert data["location"] == {
        "type": "physical",
        "web_url": None,
        "country": "Denmark",
        "state": "Capital Region",
        "city": "Copenhagen",
        "postcode": "2100",
    }
    assert data["cover_image_url"] is None
    assert data["tickets_url"] is None


def test_create_personal_event_defaults_category_to_other_for_web_location():
    """Web personal events should default the category when it is omitted."""

    user = UserFactory()
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/v1/events/",
        personal_event_payload(
            title="Digital Watch Party",
            description="A live stream for the community.",
            category=None,
            location={
                "type": "web",
                "web_url": "https://example.com/live",
            },
        ),
        format="json",
    )

    assert response.status_code == 201
    data = response.json()
    assert data["organizer_type"] == "person"
    assert data["owner_user_id"] == user.pk
    assert data["category"] == "other"
    assert data["location"] == {
        "type": "web",
        "web_url": "https://example.com/live",
        "country": None,
        "state": None,
        "city": None,
        "postcode": None,
    }


def test_create_personal_event_rejects_invalid_schedule():
    """Create should reject events whose end time is not later than the start time."""

    user = UserFactory()
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/v1/events/",
        personal_event_payload(
            title="Backwards Schedule",
            description="This should fail.",
            category="other",
            start_at="2026-05-01T20:00:00Z",
            end_at="2026-05-01T20:00:00Z",
            location={"type": "web", "web_url": "https://example.com/live"},
        ),
        format="json",
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Validation failed"
    assert data["errors"] == {
        "end_at": ["End date and time must be later than the start date and time."]
    }


def test_create_personal_event_rejects_incomplete_physical_location():
    """Physical personal events should fail without all required address parts."""

    user = UserFactory()
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/v1/events/",
        personal_event_payload(
            title="Incomplete Venue",
            description="Missing address data.",
            category="other",
            location={
                "type": "physical",
                "country": "Denmark",
                "state": "",
                "city": "Copenhagen",
                "postcode": "",
            },
        ),
        format="json",
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Validation failed"
    assert data["errors"] == {
        "location_state": ["State is required for physical event locations."],
        "location_postcode": ["Postcode or zipcode is required for physical event locations."],
    }


def test_create_owned_organization_event_returns_201_and_links_organization():
    """Owners should be able to create organization-owned events."""

    owner = UserFactory()
    organization = OrganizationFactory(owner=owner)
    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(
        "/api/v1/events/",
        organization_event_payload(
            organization_id=organization.pk,
            title="Organization Launch Party",
            description="Celebrate a new organization event.",
            category="business_networking",
        ),
        format="json",
    )

    assert response.status_code == 201
    data = response.json()
    assert data["organizer_type"] == "organization"
    assert data["owner_user_id"] is None
    assert data["organization_id"] == organization.pk
    assert data["title"] == "Organization Launch Party"
    assert data["category"] == "business_networking"


def test_create_organization_event_rejects_non_owner_with_403():
    """Non-owners should receive 403 when creating organization-owned events."""

    owner = UserFactory()
    actor = UserFactory()
    organization = OrganizationFactory(owner=owner)
    client = APIClient()
    client.force_authenticate(user=actor)

    response = client.post(
        "/api/v1/events/",
        organization_event_payload(
            organization_id=organization.pk,
            title="Unauthorized Organization Event",
            description="This should fail.",
            category="other",
        ),
        format="json",
    )

    assert response.status_code == 403
    data = response.json()
    assert data["title"] == "Forbidden"
    assert data["detail"] == "You do not have permission to create an event for this organization."
