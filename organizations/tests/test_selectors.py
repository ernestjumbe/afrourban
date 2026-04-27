"""Selector tests for organizations."""

from __future__ import annotations

import pytest

from organizations.models import OrganizationType
from organizations.selectors import organization_list
from organizations.tests.factories import OrganizationFactory
from users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_organization_list_filters_to_authenticated_owners_records():
    """owner_scope=mine should return only the requester's organizations."""

    owner = UserFactory()
    other_owner = UserFactory()
    owned = OrganizationFactory(owner=owner, name="Owned Venue")
    OrganizationFactory(owner=other_owner, name="Other Venue")

    results = list(organization_list(owner=owner, owner_scope="mine"))

    assert results == [owned]


def test_organization_list_filters_by_type_and_presence_mode():
    """Collection selectors should filter by organization type and online status."""

    matching = OrganizationFactory(
        organization_type=OrganizationType.RESTAURANT,
        is_online_only=True,
        physical_address=None,
    )
    OrganizationFactory(
        organization_type=OrganizationType.RESTAURANT,
        is_online_only=False,
        physical_address="12 Main Street",
    )
    OrganizationFactory(
        organization_type=OrganizationType.BAR,
        is_online_only=True,
        physical_address=None,
    )

    results = list(
        organization_list(
            organization_type=OrganizationType.RESTAURANT,
            is_online_only=True,
        )
    )

    assert results == [matching]


def test_organization_list_searches_name_and_description_case_insensitively():
    """Search should match against names and descriptions regardless of case."""

    name_match = OrganizationFactory(name="Midnight Collective")
    description_match = OrganizationFactory(
        name="Studio House",
        description="A COMMUNITY kitchen for local chefs.",
    )
    OrganizationFactory(name="Daylight Cafe", description="Quiet brunch spot.")

    results = list(organization_list(search="community"))

    assert results == [description_match]
    assert name_match not in results


def test_organization_list_supports_ordering_and_invalid_fallback():
    """Supported ordering should sort results; invalid ordering falls back safely."""

    alpha = OrganizationFactory(name="Alpha", created_at="2026-04-01T12:00:00Z")
    bravo = OrganizationFactory(name="Bravo", created_at="2026-04-02T12:00:00Z")

    by_name = list(organization_list(ordering="name"))
    fallback = list(organization_list(ordering="not-valid"))

    assert by_name[:2] == [alpha, bravo]
    assert fallback[:2] == [bravo, alpha]
