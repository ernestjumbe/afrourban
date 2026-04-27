"""Branding API tests for organizations."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from organizations.tests.factories import OrganizationFactory, organization_uploaded_image
from users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_owner_can_upload_logo(settings, tmp_path):
    """Owners should be able to upload a logo asset."""

    settings.MEDIA_ROOT = tmp_path
    settings.MEDIA_URL = "/media/"

    owner = UserFactory()
    organization = OrganizationFactory(owner=owner, logo=None)

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(
        f"/api/v1/organizations/{organization.pk}/logo/",
        {"logo": organization_uploaded_image(name="logo.png")},
        format="multipart",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Logo updated successfully."
    assert "/media/organizations/logos/" in data["asset_url"]


def test_owner_can_replace_existing_logo(settings, tmp_path):
    """Uploading a new logo should replace the previous stored logo."""

    settings.MEDIA_ROOT = tmp_path
    settings.MEDIA_URL = "/media/"

    owner = UserFactory()
    organization = OrganizationFactory(owner=owner, logo=None)

    client = APIClient()
    client.force_authenticate(user=owner)

    first_response = client.post(
        f"/api/v1/organizations/{organization.pk}/logo/",
        {"logo": organization_uploaded_image(name="first-logo.png")},
        format="multipart",
    )
    assert first_response.status_code == 200

    organization.refresh_from_db()
    first_logo_name = organization.logo.name

    second_response = client.post(
        f"/api/v1/organizations/{organization.pk}/logo/",
        {"logo": organization_uploaded_image(name="second-logo.png")},
        format="multipart",
    )

    assert second_response.status_code == 200
    organization.refresh_from_db()
    assert organization.logo is not None
    assert organization.logo.name != first_logo_name


def test_owner_can_delete_logo(settings, tmp_path):
    """Owners should be able to delete an uploaded logo."""

    settings.MEDIA_ROOT = tmp_path
    settings.MEDIA_URL = "/media/"

    owner = UserFactory()
    organization = OrganizationFactory(owner=owner, logo=None)

    client = APIClient()
    client.force_authenticate(user=owner)

    upload_response = client.post(
        f"/api/v1/organizations/{organization.pk}/logo/",
        {"logo": organization_uploaded_image(name="delete-logo.png")},
        format="multipart",
    )
    assert upload_response.status_code == 200

    response = client.delete(f"/api/v1/organizations/{organization.pk}/logo/")

    assert response.status_code == 204
    organization.refresh_from_db()
    assert not organization.logo


def test_owner_can_upload_cover_image(settings, tmp_path):
    """Owners should be able to upload a cover image asset."""

    settings.MEDIA_ROOT = tmp_path
    settings.MEDIA_URL = "/media/"

    owner = UserFactory()
    organization = OrganizationFactory(owner=owner, cover_image=None)

    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(
        f"/api/v1/organizations/{organization.pk}/cover/",
        {"cover_image": organization_uploaded_image(name="cover.png")},
        format="multipart",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Cover image updated successfully."
    assert "/media/organizations/covers/" in data["asset_url"]


def test_branding_upload_rejects_invalid_file_type(settings, tmp_path):
    """Branding uploads should reject unsupported file types."""

    settings.MEDIA_ROOT = tmp_path
    settings.MEDIA_URL = "/media/"

    owner = UserFactory()
    organization = OrganizationFactory(owner=owner)

    client = APIClient()
    client.force_authenticate(user=owner)

    invalid_file = organization_uploaded_image(
        name="logo.txt",
        content_type="text/plain",
    )
    response = client.post(
        f"/api/v1/organizations/{organization.pk}/logo/",
        {"logo": invalid_file},
        format="multipart",
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Validation failed"
    assert data["errors"] == {
        "logo": ["Unsupported file format. Use JPEG, PNG, or WebP."]
    }


def test_non_owner_logo_upload_returns_403(settings, tmp_path):
    """Non-owners should not be able to change organization branding."""

    settings.MEDIA_ROOT = tmp_path
    settings.MEDIA_URL = "/media/"

    owner = UserFactory()
    viewer = UserFactory()
    organization = OrganizationFactory(owner=owner)

    client = APIClient()
    client.force_authenticate(user=viewer)

    response = client.post(
        f"/api/v1/organizations/{organization.pk}/logo/",
        {"logo": organization_uploaded_image(name="blocked-logo.png")},
        format="multipart",
    )

    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "You do not have permission to modify this organization."
