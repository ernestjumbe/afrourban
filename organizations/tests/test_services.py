"""Service-layer tests for organizations."""

from __future__ import annotations

import pytest
from rest_framework.exceptions import PermissionDenied, ValidationError

from organizations.models import OrganizationType
from organizations.services import organization_create, organization_update
from organizations.tests.factories import OrganizationFactory
from users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_organization_create_persists_owner_and_normalized_fields():
    """Creation should assign the owner and normalize persisted strings."""

    owner = UserFactory()

    organization = organization_create(
        owner=owner,
        name="  Community Kitchen  ",
        description="A neighborhood food collective.",
        organization_type=OrganizationType.RESTAURANT,
        is_online_only=False,
        physical_address="  10 Example Road  ",
    )

    assert organization.pk is not None
    assert organization.owner_id == owner.pk
    assert organization.name == "Community Kitchen"
    assert organization.description == "A neighborhood food collective."
    assert organization.organization_type == OrganizationType.RESTAURANT
    assert organization.is_online_only is False
    assert organization.physical_address == "10 Example Road"


def test_organization_create_rejects_case_insensitive_duplicate_name_for_owner():
    """A single owner should not be able to reuse the same organization name."""

    owner = UserFactory()
    OrganizationFactory(owner=owner, name="Midnight Collective")

    with pytest.raises(ValidationError) as exc_info:
        organization_create(
            owner=owner,
            name="  midnight collective  ",
            description="Late-night arts community.",
            organization_type=OrganizationType.OTHER,
            is_online_only=True,
            physical_address=None,
        )

    assert exc_info.value.detail == {
        "name": ["You already have an organization with this name."]
    }


def test_organization_create_requires_physical_address_for_physical_presence():
    """Physical organizations must provide an address on create."""

    owner = UserFactory()

    with pytest.raises(ValidationError) as exc_info:
        organization_create(
            owner=owner,
            name="Barbershop Union",
            description="A collective for barbers in the city.",
            organization_type=OrganizationType.BARBER,
            is_online_only=False,
            physical_address="  ",
        )

    assert exc_info.value.detail == {
        "physical_address": [
            "Physical address is required for organizations with a physical presence."
        ]
    }


def test_organization_update_persists_requested_metadata_changes():
    """Owners should be able to update core organization metadata."""

    owner = UserFactory()
    organization = OrganizationFactory(
        owner=owner,
        name="Original Name",
        description="Original description.",
        organization_type=OrganizationType.RESTAURANT,
        is_online_only=False,
        physical_address="100 First Street",
    )

    updated = organization_update(
        organization=organization,
        actor=owner,
        name="  Updated Name  ",
        description="Updated description.",
        organization_type=OrganizationType.EVENT_ORGANIZER,
    )

    assert updated.name == "Updated Name"
    assert updated.description == "Updated description."
    assert updated.organization_type == OrganizationType.EVENT_ORGANIZER
    assert updated.is_online_only is False
    assert updated.physical_address == "100 First Street"


def test_organization_update_clears_address_when_switching_to_online_only():
    """Switching an organization online-only should clear its address."""

    owner = UserFactory()
    organization = OrganizationFactory(
        owner=owner,
        is_online_only=False,
        physical_address="88 Venue Row",
    )

    updated = organization_update(
        organization=organization,
        actor=owner,
        is_online_only=True,
    )

    assert updated.is_online_only is True
    assert updated.physical_address is None


def test_organization_update_rejects_non_owner_actor():
    """Only owners or admins should be able to update organizations."""

    owner = UserFactory()
    viewer = UserFactory()
    organization = OrganizationFactory(owner=owner)

    with pytest.raises(PermissionDenied) as exc_info:
        organization_update(
            organization=organization,
            actor=viewer,
            description="Unauthorized edit.",
        )

    assert str(exc_info.value.detail) == "You do not have permission to modify this organization."
