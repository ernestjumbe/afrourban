"""Tests for API deprecation policy validation rules."""

from __future__ import annotations

import pytest

from afrourban.api_governance import (
    DeprecationPolicyError,
    validate_deprecation_entry,
    validate_deprecation_registry,
)
from users.tests.factories import deprecation_notice_entry, deprecation_registry_payload


def test_deprecation_entry_accepts_exact_90_day_notice_window():
    """The default policy accepts an exact 90-day notice period."""

    entry = deprecation_notice_entry(
        deprecation_date="2026-01-01",
        removal_date="2026-04-01",
    )

    validate_deprecation_entry(entry)


def test_deprecation_entry_rejects_notice_window_below_90_days():
    """Entries below the 90-day minimum must fail validation."""

    entry = deprecation_notice_entry(
        deprecation_date="2026-01-01",
        removal_date="2026-03-31",
    )

    with pytest.raises(DeprecationPolicyError, match="at least 90 days"):
        validate_deprecation_entry(entry)


def test_deprecation_entry_requires_migration_path():
    """Missing migration guidance is invalid for deprecated entries."""

    entry = deprecation_notice_entry(
        migration_path="",
    )

    with pytest.raises(DeprecationPolicyError, match="migration_path"):
        validate_deprecation_entry(entry)


def test_registry_policy_override_enforces_custom_notice_window():
    """Policy-level minimum_notice_days overrides the default 90-day rule."""

    entry = deprecation_notice_entry(
        deprecation_date="2026-01-01",
        removal_date="2026-04-01",
    )
    registry = deprecation_registry_payload(
        endpoints=[entry],
        minimum_notice_days=120,
    )

    with pytest.raises(DeprecationPolicyError, match="at least 120 days"):
        validate_deprecation_registry(registry)


def test_active_entries_without_dates_are_allowed():
    """Active entries do not require deprecation fields."""

    registry = {
        "policy": {"minimum_notice_days": 90},
        "versions": [
            {
                "target_type": "version",
                "target_id": "v1",
                "status": "active",
                "deprecation_date": None,
                "removal_date": None,
                "migration_path": None,
            }
        ],
        "endpoints": [],
    }

    validate_deprecation_registry(registry)
