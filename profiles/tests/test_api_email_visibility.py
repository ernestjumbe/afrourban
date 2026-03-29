"""Profile API ownership visibility tests (feature 006)."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from profiles.tests.factories import ProfileFactory
from users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_profile_me_includes_email_for_owner():
    """The authenticated user's profile should include email."""

    user = UserFactory(email="owner@example.com")
    ProfileFactory(user=user)

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/v1/profiles/me/")

    assert response.status_code == 200
    assert response.json()["email"] == "owner@example.com"


def test_profile_public_endpoint_includes_email_for_owned_profile():
    """Owned profile payloads should include email on the public endpoint."""

    user = UserFactory(email="self-view@example.com")
    ProfileFactory(user=user)

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(f"/api/v1/profiles/{user.pk}/")

    assert response.status_code == 200
    assert response.json()["email"] == "self-view@example.com"


def test_profile_public_endpoint_omits_email_for_non_owned_profile():
    """Non-owned public profiles should redact email."""

    viewer = UserFactory(email="viewer@example.com")
    subject = UserFactory(email="subject@example.com")
    ProfileFactory(user=viewer)
    ProfileFactory(user=subject)

    client = APIClient()
    client.force_authenticate(user=viewer)

    response = client.get(f"/api/v1/profiles/{subject.pk}/")

    assert response.status_code == 200
    assert "email" not in response.json()
