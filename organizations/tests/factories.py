"""Test factories and helpers for organizations."""

from __future__ import annotations

import base64

import factory
from django.core.files.uploadedfile import SimpleUploadedFile

from organizations.models import Organization, OrganizationType
from users.tests.factories import UserFactory

_PNG_1X1_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+c4Z8AAAAASUVORK5CYII="
)


class OrganizationFactory(factory.django.DjangoModelFactory):
    """Factory for creating Organization instances in tests."""

    class Meta:
        model = Organization

    owner = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"Organization {n}")
    description = factory.Faker("text", max_nb_chars=200)
    organization_type = OrganizationType.RESTAURANT
    is_online_only = False
    physical_address = factory.Sequence(lambda n: f"{n} Example Street")
    logo = None
    cover_image = None


def organization_payload(
    *,
    name: str = "Community Kitchen",
    description: str = "A neighborhood food collective.",
    organization_type: str = "restaurant",
    is_online_only: bool = False,
    physical_address: str | None = "10 Example Road",
) -> dict[str, object]:
    """Build an organization create payload for tests."""

    return {
        "name": name,
        "description": description,
        "organization_type": organization_type,
        "is_online_only": is_online_only,
        "physical_address": physical_address,
    }


def organization_update_payload(
    *,
    name: str = "Updated Community Kitchen",
    description: str = "Updated organization description.",
    organization_type: str = "other",
    is_online_only: bool = True,
    physical_address: str | None = None,
) -> dict[str, object]:
    """Build an organization update payload for tests."""

    return {
        "name": name,
        "description": description,
        "organization_type": organization_type,
        "is_online_only": is_online_only,
        "physical_address": physical_address,
    }


def organization_uploaded_image(
    *,
    name: str = "organization.png",
    content_type: str = "image/png",
) -> SimpleUploadedFile:
    """Create a minimal valid uploaded image file for tests."""

    return SimpleUploadedFile(
        name=name,
        content=_PNG_1X1_BYTES,
        content_type=content_type,
    )
