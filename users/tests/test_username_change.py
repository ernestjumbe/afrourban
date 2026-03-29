"""Username change and cooldown tests (feature 006)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone as dt_timezone
from typing import TYPE_CHECKING, cast

import pytest
from django.test import override_settings
from django.utils.dateparse import parse_datetime
from rest_framework.test import APIClient

from users.tests.factories import UserFactory, username_change_payload

if TYPE_CHECKING:
    from users.models import CustomUser

pytestmark = pytest.mark.django_db

FIXED_NOW = datetime(2026, 3, 28, 12, 0, tzinfo=dt_timezone.utc)


def _freeze_username_time(monkeypatch, now: datetime = FIXED_NOW) -> datetime:
    from users import services as user_services

    monkeypatch.setattr(user_services.timezone, "now", lambda: now)
    return now


def test_first_username_change_succeeds_and_starts_cooldown(monkeypatch):
    """The first post-registration username change should succeed."""

    now = _freeze_username_time(monkeypatch)
    user = UserFactory(username="first@example.com")

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(
        "/api/v1/auth/username/",
        username_change_payload(username="fresh_name"),
        format="json",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user.pk
    assert data["username"] == "fresh_name"
    assert data["cooldown_days"] == 7
    assert parse_datetime(data["next_allowed_at"]) == now + timedelta(days=7)

    user.refresh_from_db()
    assert user.username == "fresh_name"
    assert user.username_changed_at == now


def test_username_change_is_rejected_while_cooldown_is_active(monkeypatch):
    """A second change before cooldown expiry should be blocked."""

    now = _freeze_username_time(monkeypatch)
    user = UserFactory(
        username="current_name",
        username_changed_at=now - timedelta(days=1),
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(
        "/api/v1/auth/username/",
        username_change_payload(username="second_name"),
        format="json",
    )

    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "cooldown_active"
    expected_next_allowed_at = now + timedelta(days=6)
    assert expected_next_allowed_at.isoformat() in data["detail"]

    user.refresh_from_db()
    assert user.username == "current_name"
    assert user.username_changed_at == now - timedelta(days=1)


def test_username_change_succeeds_after_cooldown_expires(monkeypatch):
    """Changes should be allowed once the cooldown window has passed."""

    now = _freeze_username_time(monkeypatch)
    user = UserFactory(
        username="after_window",
        username_changed_at=now - timedelta(days=8),
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(
        "/api/v1/auth/username/",
        username_change_payload(username="expired_window"),
        format="json",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "expired_window"
    assert data["cooldown_days"] == 7
    assert parse_datetime(data["next_allowed_at"]) == now + timedelta(days=7)


@override_settings(USERS_USERNAME_CHANGE_COOLDOWN_DAYS=2)
def test_username_change_honors_configured_cooldown_days(monkeypatch):
    """Cooldown evaluation should use the configured day count."""

    now = _freeze_username_time(monkeypatch)
    user = UserFactory(
        username="configurable_name",
        username_changed_at=now - timedelta(days=1),
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(
        "/api/v1/auth/username/",
        username_change_payload(username="configurable_next"),
        format="json",
    )

    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "cooldown_active"
    expected_next_allowed_at = now + timedelta(days=1)
    assert expected_next_allowed_at.isoformat() in data["detail"]


@pytest.mark.parametrize(
    ("requested_username", "expected_error"),
    [
        (
            "bad-name",
            "Username must be 3-30 characters, contain at least one letter, "
            "not start with '.', and use only letters, numbers, '_' or '.'.",
        ),
        ("taken_name", "This username is already in use."),
    ],
)
def test_username_change_rejects_invalid_format_and_duplicates(
    requested_username: str,
    expected_error: str,
    monkeypatch,
):
    """Invalid and duplicate username changes should be rejected."""

    _freeze_username_time(monkeypatch)
    user = cast("CustomUser", UserFactory(username="original_name"))
    if requested_username == "taken_name":
        UserFactory(username="taken_name")

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(
        "/api/v1/auth/username/",
        username_change_payload(username=requested_username),
        format="json",
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Validation failed"
    assert data["errors"] == {"username": [expected_error]}

    user.refresh_from_db()
    assert user.username == "original_name"
    assert user.username_changed_at is None
