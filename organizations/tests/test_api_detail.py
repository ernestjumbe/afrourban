"""Detail API tests for organizations."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from organizations.models import OrganizationType
from organizations.tests.factories import OrganizationFactory, organization_uploaded_image
from users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_owner_can_patch_organization_metadata():
    """Owners should be able to patch organization metadata."""

    owner = UserFactory()
    organization = OrganizationFactory(
        owner=owner,
        name="Original Venue",
        description="Original description.",
        organization_type=OrganizationType.BAR,
        is_online_only=False,
        physical_address="123 Original Road",
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.patch(
        f"/api/v1/organizations/{organization.pk}/",
        {
            "name": "Updated Venue",
            "description": "Updated description.",
            "organization_type": OrganizationType.NIGHT_CLUB,
        },
        format="json",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == organization.pk
    assert data["owner_id"] == owner.pk
    assert data["name"] == "Updated Venue"
    assert data["description"] == "Updated description."
    assert data["organization_type"] == OrganizationType.NIGHT_CLUB
    assert data["physical_address"] == "123 Original Road"


def test_owner_patch_can_switch_organization_to_online_only():
    """Owners should be able to toggle presence mode to online-only."""

    owner = UserFactory()
    organization = OrganizationFactory(
        owner=owner,
        is_online_only=False,
        physical_address="500 Studio Lane",
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.patch(
        f"/api/v1/organizations/{organization.pk}/",
        {"is_online_only": True},
        format="json",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_online_only"] is True
    assert data["physical_address"] is None


def test_non_owner_patch_returns_403():
    """Non-owners should not be able to patch organization metadata."""

    owner = UserFactory()
    viewer = UserFactory()
    organization = OrganizationFactory(owner=owner)

    client = APIClient()
    client.force_authenticate(user=viewer)

    response = client.patch(
        f"/api/v1/organizations/{organization.pk}/",
        {"description": "Unauthorized update."},
        format="json",
    )

    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "You do not have permission to modify this organization."


def test_authenticated_viewer_can_get_organization_detail_with_organization_fields(
    settings, tmp_path
):
    """Detail GET should return organization-only fields for authenticated viewers."""

    settings.MEDIA_ROOT = tmp_path
    settings.MEDIA_URL = "/media/"

    owner = UserFactory()
    viewer = UserFactory()
    organization = OrganizationFactory(
        owner=owner,
        name="Digital Dance Hub",
        description="A remote-first dance collective.",
        organization_type=OrganizationType.DANCE_CREW,
        is_online_only=True,
        physical_address=None,
    )
    organization.logo.save(
        "logo.png",
        organization_uploaded_image(name="logo.png"),
        save=True,
    )
    organization.cover_image.save(
        "cover.png",
        organization_uploaded_image(name="cover.png"),
        save=True,
    )

    client = APIClient()
    client.force_authenticate(user=viewer)

    response = client.get(f"/api/v1/organizations/{organization.pk}/")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == organization.pk
    assert data["owner_id"] == owner.pk
    assert data["name"] == "Digital Dance Hub"
    assert data["description"] == "A remote-first dance collective."
    assert data["organization_type"] == OrganizationType.DANCE_CREW
    assert data["is_online_only"] is True
    assert data["physical_address"] is None
    assert data["logo_url"].endswith(organization.logo.url)
    assert data["cover_image_url"].endswith(organization.cover_image.url)
    assert "email" not in data
    assert "display_name" not in data
