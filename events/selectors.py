"""Selectors for event read operations."""

from events.models import Event


def event_get_by_id(*, event_id: int) -> Event:
    """Return one event with its organizer relations loaded."""

    return Event.objects.select_related(
        "owner",
        "organization",
        "organization__owner",
    ).prefetch_related(
        "audit_entries",
    ).get(pk=event_id)
