"""Cover-image API tests for events."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from events.tests.factories import EventFactory, event_uploaded_image
from users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_owner_can_upload_event_cover_image(settings, tmp_path):
    """Owners should be able to upload an event cover image."""

    settings.MEDIA_ROOT = tmp_path
    settings.MEDIA_URL = "/media/"

    owner = UserFactory()
    event = EventFactory(owner=owner, organization=None, cover_image=None)
    client = APIClient()
    client.force_authenticate(user=owner)

    response = client.post(
        f"/api/v1/events/{event.pk}/cover/",
        {"cover_image": event_uploaded_image(name="cover.png")},
        format="multipart",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Cover image updated successfully."
    assert "/media/events/covers/" in data["asset_url"]


def test_owner_can_replace_existing_event_cover_image(settings, tmp_path):
    """Uploading a new event cover should replace the previous stored file."""

    settings.MEDIA_ROOT = tmp_path
    settings.MEDIA_URL = "/media/"

    owner = UserFactory()
    event = EventFactory(owner=owner, organization=None, cover_image=None)
    client = APIClient()
    client.force_authenticate(user=owner)

    first_response = client.post(
        f"/api/v1/events/{event.pk}/cover/",
        {"cover_image": event_uploaded_image(name="first-cover.png")},
        format="multipart",
    )
    assert first_response.status_code == 200

    event.refresh_from_db()
    first_cover_name = event.cover_image.name

    second_response = client.post(
        f"/api/v1/events/{event.pk}/cover/",
        {"cover_image": event_uploaded_image(name="second-cover.png")},
        format="multipart",
    )

    assert second_response.status_code == 200
    event.refresh_from_db()
    assert event.cover_image is not None
    assert event.cover_image.name != first_cover_name


def test_owner_can_delete_event_cover_image(settings, tmp_path):
    """Owners should be able to delete an uploaded event cover image."""

    settings.MEDIA_ROOT = tmp_path
    settings.MEDIA_URL = "/media/"

    owner = UserFactory()
    event = EventFactory(owner=owner, organization=None, cover_image=None)
    client = APIClient()
    client.force_authenticate(user=owner)

    upload_response = client.post(
        f"/api/v1/events/{event.pk}/cover/",
        {"cover_image": event_uploaded_image(name="delete-cover.png")},
        format="multipart",
    )
    assert upload_response.status_code == 200

    response = client.delete(f"/api/v1/events/{event.pk}/cover/")

    assert response.status_code == 204
    event.refresh_from_db()
    assert not event.cover_image


def test_cover_upload_rejects_invalid_file_type(settings, tmp_path):
    """Cover uploads should reject unsupported image formats."""

    settings.MEDIA_ROOT = tmp_path
    settings.MEDIA_URL = "/media/"

    owner = UserFactory()
    event = EventFactory(owner=owner, organization=None)
    client = APIClient()
    client.force_authenticate(user=owner)

    invalid_file = event_uploaded_image(
        name="cover.txt",
        content_type="text/plain",
    )
    response = client.post(
        f"/api/v1/events/{event.pk}/cover/",
        {"cover_image": invalid_file},
        format="multipart",
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Validation failed"
    assert data["errors"] == {
        "cover_image": ["Unsupported file format. Use JPEG, PNG, or WebP."]
    }


def test_non_owner_cover_upload_returns_403(settings, tmp_path):
    """Non-owners should not be able to mutate event cover images."""

    settings.MEDIA_ROOT = tmp_path
    settings.MEDIA_URL = "/media/"

    owner = UserFactory()
    viewer = UserFactory()
    event = EventFactory(owner=owner, organization=None)
    client = APIClient()
    client.force_authenticate(user=viewer)

    response = client.post(
        f"/api/v1/events/{event.pk}/cover/",
        {"cover_image": event_uploaded_image(name="blocked-cover.png")},
        format="multipart",
    )

    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "You do not have permission to modify this event."
