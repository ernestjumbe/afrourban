"""Registration tests for username registration rollout (feature 006)."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from users.tests.factories import UserFactory, registration_payload

pytestmark = pytest.mark.django_db

User = get_user_model()


class TestRegisterUsernameValidation:
    """Registration should require and persist a valid username."""

    def test_register_with_valid_username_persists_username(self):
        payload = registration_payload(
            email="valid-registration@example.com",
            username="valid_candidate",
        )

        client = APIClient()
        response = client.post("/api/v1/auth/register/", payload, format="json")

        assert response.status_code == 201
        user = User.objects.get(email__iexact=payload["email"])
        assert user.username == payload["username"]

    def test_register_without_username_returns_400(self):
        payload = registration_payload(email="missing-username@example.com")
        payload.pop("username")

        client = APIClient()
        response = client.post("/api/v1/auth/register/", payload, format="json")

        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Validation failed"
        assert data["errors"] == {"username": ["This field is required."]}

    @pytest.mark.parametrize(
        "username",
        ["12", ".leadingdot", "1234", "bad-name"],
    )
    def test_register_with_invalid_username_returns_400(self, username: str):
        payload = registration_payload(
            email=f"{username.replace('.', 'dot').replace('-', 'dash')}@example.com",
            username=username,
        )

        client = APIClient()
        response = client.post("/api/v1/auth/register/", payload, format="json")

        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Validation failed"
        assert data["errors"] == {
            "username": [
                "Username must be 3-30 characters, contain at least one letter, "
                "not start with '.', and use only letters, numbers, '_' or '.'."
            ]
        }


class TestRegisterUsernameUniqueness:
    """Registration should enforce case-insensitive username uniqueness."""

    def test_register_with_case_insensitive_username_collision_returns_400(self):
        UserFactory(username="Taken.Name", email="existing@example.com")
        payload = registration_payload(
            email="new-candidate@example.com",
            username="taken.name",
        )

        client = APIClient()
        response = client.post("/api/v1/auth/register/", payload, format="json")

        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Validation failed"
        assert data["errors"] == {"username": ["This username is already in use."]}
        assert not User.objects.filter(email__iexact=payload["email"]).exists()


class TestTokenAuthenticationRegression:
    """Email/password authentication must remain unchanged by username rollout."""

    def test_token_login_still_uses_email_and_password(self):
        user = UserFactory(
            email="login@example.com",
            username="login_name",
            is_email_verified=True,
        )
        user.set_password("TestPass123!")
        user.save(update_fields=["password"])

        client = APIClient()
        response = client.post(
            "/api/v1/auth/token/",
            {"email": user.email, "password": "TestPass123!"},
            format="json",
        )

        assert response.status_code == 200
        data = response.json()
        assert "access" in data
        assert "refresh" in data
        assert data["user"]["email"] == user.email
