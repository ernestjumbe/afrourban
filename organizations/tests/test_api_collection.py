"""Collection API tests for organizations."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from organizations.tests.factories import OrganizationFactory, organization_payload
from users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_create_organization_returns_201_and_assigns_authenticated_owner():
    """Authenticated users should be able to create physical organizations."""

    user = UserFactory()
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/v1/organizations/",
        organization_payload(),
        format="json",
    )

    assert response.status_code == 201
    data = response.json()
    assert data["owner_id"] == user.pk
    assert data["name"] == "Community Kitchen"
    assert data["description"] == "A neighborhood food collective."
    assert data["organization_type"] == "restaurant"
    assert data["is_online_only"] is False
    assert data["physical_address"] == "10 Example Road"
    assert data["logo_url"] is None
    assert data["cover_image_url"] is None


def test_create_online_only_organization_allows_blank_physical_address():
    """Online-only organizations should not require a physical address."""

    user = UserFactory()
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/v1/organizations/",
        organization_payload(
            name="Digital Dance Hub",
            organization_type="online_community",
            is_online_only=True,
            physical_address="",
        ),
        format="json",
    )

    assert response.status_code == 201
    data = response.json()
    assert data["owner_id"] == user.pk
    assert data["name"] == "Digital Dance Hub"
    assert data["is_online_only"] is True
    assert data["physical_address"] is None


def test_create_organization_rejects_same_owner_duplicate_name():
    """Duplicate organization names should be rejected per owner."""

    user = UserFactory()
    OrganizationFactory(owner=user, name="Night Market")

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/v1/organizations/",
        organization_payload(
            name="  night market  ",
            description="Duplicate entry attempt.",
            organization_type="retail_store",
            is_online_only=True,
            physical_address=None,
        ),
        format="json",
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Validation failed"
    assert data["errors"] == {
        "name": ["You already have an organization with this name."]
    }


def test_create_organization_requires_address_when_not_online_only():
    """Physical organizations should fail validation without an address."""

    user = UserFactory()
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/v1/organizations/",
        organization_payload(
            name="Downtown Barbers",
            organization_type="barber",
            is_online_only=False,
            physical_address="",
        ),
        format="json",
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Validation failed"
    assert data["errors"] == {
        "physical_address": [
            "Physical address is required for organizations with a physical presence."
        ]
    }


def test_list_organizations_returns_paginated_filtered_results():
    """Collection GET should use the documented pagination and filter contract."""

    owner = UserFactory()
    other_owner = UserFactory()
    alpha = OrganizationFactory(
        owner=owner,
        name="Alpha Kitchen",
        description="Shared kitchen for creators.",
        organization_type="restaurant",
        is_online_only=True,
        physical_address=None,
    )
    bravo = OrganizationFactory(
        owner=owner,
        name="Bravo Kitchen",
        description="Shared kitchen for the community.",
        organization_type="restaurant",
        is_online_only=True,
        physical_address=None,
    )
    OrganizationFactory(
        owner=owner,
        name="Physical Kitchen",
        organization_type="restaurant",
        is_online_only=False,
        physical_address="44 Main Street",
    )
    OrganizationFactory(
        owner=other_owner,
        name="Other Owner Kitchen",
        organization_type="restaurant",
        is_online_only=True,
        physical_address=None,
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.get(
        "/api/v1/organizations/",
        {
            "owner_scope": "mine",
            "organization_type": "restaurant",
            "is_online_only": "true",
            "ordering": "name",
            "page": 1,
            "page_size": 1,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert data["previous"] is None
    assert "page=2" in data["next"]
    assert data["results"][0]["id"] == alpha.pk
    assert data["results"][0]["owner_id"] == owner.pk
    assert data["results"][0]["name"] == "Alpha Kitchen"
    assert data["results"][0]["physical_address"] is None
    assert data["results"][0]["logo_url"] is None
    assert data["results"][0]["cover_image_url"] is None
    assert data["results"][0]["description"] == "Shared kitchen for creators."
    assert data["results"][0]["organization_type"] == "restaurant"

    response_page_2 = client.get(
        "/api/v1/organizations/",
        {
            "owner_scope": "mine",
            "organization_type": "restaurant",
            "is_online_only": "true",
            "ordering": "name",
            "page": 2,
            "page_size": 1,
        },
    )

    assert response_page_2.status_code == 200
    page_2 = response_page_2.json()
    assert "page=1" in page_2["previous"]
    assert page_2["next"] is None
    assert page_2["results"][0]["id"] == bravo.pk
