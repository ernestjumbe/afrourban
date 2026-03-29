"""API email visibility projection tests (feature 006)."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from profiles.tests.factories import ProfileFactory
from users.tests.factories import StaffUserFactory, UserFactory, registration_payload

pytestmark = pytest.mark.django_db


def test_non_privileged_user_does_not_receive_non_owned_email():
    """Non-owned public profile payloads should omit email."""

    viewer = UserFactory()
    subject = UserFactory(email="subject@example.com")
    ProfileFactory(user=viewer)
    ProfileFactory(user=subject)

    client = APIClient()
    client.force_authenticate(user=viewer)

    response = client.get(f"/api/v1/profiles/{subject.pk}/")

    assert response.status_code == 200
    assert "email" not in response.json()


def test_registration_response_keeps_owned_email_visible():
    """Owned user payloads should keep email visible."""

    client = APIClient()
    response = client.post(
        "/api/v1/auth/register/",
        registration_payload(
            email="owned@example.com",
            username="owned_user",
        ),
        format="json",
    )

    assert response.status_code == 201
    assert response.json()["email"] == "owned@example.com"


def test_admin_user_detail_keeps_email_visible_for_staff():
    """Authorized staff operations should retain non-owned email visibility."""

    staff_user = StaffUserFactory()
    subject = UserFactory(email="managed-user@example.com")
    ProfileFactory(user=staff_user)
    ProfileFactory(user=subject)

    client = APIClient()
    client.force_authenticate(user=staff_user)

    response = client.get(f"/api/v1/admin/users/{subject.pk}/")

    assert response.status_code == 200
    assert response.json()["email"] == "managed-user@example.com"
