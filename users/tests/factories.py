"""Test factories for users app."""

from __future__ import annotations

import secrets
from datetime import date, timedelta
from typing import TYPE_CHECKING

import factory
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

if TYPE_CHECKING:
    from users.models import CustomUser


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating CustomUser instances in tests."""

    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.LazyAttribute(lambda obj: obj.email)
    password = factory.PostGenerationMethodCall("set_password", "TestPass123!")
    is_active = True
    is_staff = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override create to use the manager's create_user method."""
        password = kwargs.pop("password", None)
        obj = super()._create(model_class, *args, **kwargs)
        if password:
            obj.set_password(password)
            obj.save()
        return obj


class StaffUserFactory(UserFactory):
    """Factory for creating staff users in tests."""

    is_staff = True


class EmailVerificationTokenFactory(factory.django.DjangoModelFactory):
    """Factory for creating EmailVerificationToken instances in tests."""

    class Meta:
        model = "users.EmailVerificationToken"

    user = factory.SubFactory(UserFactory)
    token = factory.LazyFunction(lambda: secrets.token_urlsafe(32))
    expires_at = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))


class WebAuthnCredentialFactory(factory.django.DjangoModelFactory):
    """Factory for creating WebAuthnCredential instances in tests."""

    class Meta:
        model = "users.WebAuthnCredential"

    user = factory.SubFactory(UserFactory)
    credential_id = factory.LazyFunction(lambda: secrets.token_bytes(64))
    public_key = factory.LazyFunction(lambda: secrets.token_bytes(77))
    sign_count = 0
    webauthn_user_id = factory.LazyFunction(lambda: secrets.token_bytes(64))
    device_label = factory.Sequence(lambda n: f"Device {n}")
    is_enabled = True


def registration_payload(
    *,
    email: str = "candidate@example.com",
    password: str = "TestPass123!",
    username: str = "candidate_1",
    display_name: str = "Candidate",
) -> dict[str, str]:
    """Build a registration payload for username-aware tests."""

    return {
        "email": email,
        "password": password,
        "password_confirm": password,
        "username": username,
        "display_name": display_name,
    }


def username_change_payload(*, username: str = "updated_name") -> dict[str, str]:
    """Build a username-change payload."""

    return {"username": username}


def ownership_case(
    *,
    viewer: "CustomUser",
    subject: "CustomUser",
) -> dict[str, int | bool]:
    """Build ownership context for privacy projection tests."""

    return {
        "viewer_id": viewer.pk,
        "subject_id": subject.pk,
        "is_owned": viewer.pk == subject.pk,
        "viewer_is_staff": bool(viewer.is_staff),
    }


def deprecation_notice_entry(
    *,
    target_type: str = "endpoint",
    target_id: str = "auth.register",
    status: str = "deprecated",
    deprecation_date: str | None = None,
    removal_date: str | None = None,
    migration_path: str = "/api/v1/auth/register/",
) -> dict[str, str]:
    """Create a deprecation notice payload for governance tests."""

    dep_date = deprecation_date or date.today().isoformat()
    rem_date = removal_date or (date.today() + timedelta(days=90)).isoformat()
    return {
        "target_type": target_type,
        "target_id": target_id,
        "status": status,
        "deprecation_date": dep_date,
        "removal_date": rem_date,
        "migration_path": migration_path,
    }


def deprecation_registry_payload(
    *,
    versions: list[dict[str, str]] | None = None,
    endpoints: list[dict[str, str]] | None = None,
    minimum_notice_days: int = 90,
) -> dict[str, object]:
    """Create a full deprecation registry payload for tests."""

    return {
        "policy": {
            "minimum_notice_days": minimum_notice_days,
            "required_fields": [
                "deprecation_date",
                "removal_date",
                "migration_path",
            ],
        },
        "versions": versions or [],
        "endpoints": endpoints or [],
    }
