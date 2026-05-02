"""Selector tests for events."""

from __future__ import annotations

import pytest

from events.models import EventAuditEntry, EventAuditField
from events.selectors import event_get_by_id
from events.tests.factories import EventFactory, OrganizationEventFactory
from users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_event_get_by_id_returns_personal_event_with_owner_relation():
    """Detail selectors should load the personal owner relation."""

    event = EventFactory()

    selected = event_get_by_id(event_id=event.pk)

    assert selected.pk == event.pk
    assert selected.owner.pk == event.owner.pk
    assert selected.organization is None
    assert selected.organizer_type == "person"


def test_event_get_by_id_returns_organization_event_with_audit_entries():
    """Detail selectors should load organization context and attached audits."""

    actor = UserFactory()
    event = OrganizationEventFactory()
    audit_entry = EventAuditEntry.objects.create(
        event=event,
        actor=actor,
        field_name=EventAuditField.TITLE,
        old_value="Original Event Title",
        new_value="Updated Event Title",
    )

    selected = event_get_by_id(event_id=event.pk)

    assert selected.pk == event.pk
    assert selected.owner is None
    assert selected.organization.pk == event.organization.pk
    assert selected.organization.owner.pk == event.organization.owner.pk
    assert list(selected.audit_entries.all()) == [audit_entry]
