"""Utilities for API governance and deprecation policy validation."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any, Mapping

import yaml

DEFAULT_MINIMUM_NOTICE_DAYS = 90
REQUIRED_DEPRECATION_FIELDS = ("deprecation_date", "removal_date", "migration_path")
DEFAULT_DEPRECATION_REGISTRY_PATH = (
    Path(__file__).resolve().parent.parent / "docs" / "api" / "deprecations.yaml"
)


class DeprecationPolicyError(ValueError):
    """Raised when deprecation policy metadata is invalid."""


def parse_iso_date(value: str, *, field_name: str) -> date:
    """Parse a strict ISO date string."""

    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise DeprecationPolicyError(f"{field_name} must be ISO date (YYYY-MM-DD).") from exc


def validate_notice_window(
    deprecation_date: date,
    removal_date: date,
    *,
    minimum_notice_days: int = DEFAULT_MINIMUM_NOTICE_DAYS,
) -> None:
    """Ensure removal date satisfies the minimum notice window."""

    min_removal_date = deprecation_date + timedelta(days=minimum_notice_days)
    if removal_date < min_removal_date:
        raise DeprecationPolicyError(
            "removal_date must be at least "
            f"{minimum_notice_days} days after deprecation_date."
        )


def _requires_validation(entry: Mapping[str, Any]) -> bool:
    status = str(entry.get("status", "")).lower()
    if status in {"deprecated", "retired", "announced"}:
        return True

    return any(entry.get(field) not in (None, "") for field in REQUIRED_DEPRECATION_FIELDS)


def validate_deprecation_entry(
    entry: Mapping[str, Any],
    *,
    minimum_notice_days: int = DEFAULT_MINIMUM_NOTICE_DAYS,
) -> None:
    """Validate one version/endpoint deprecation entry."""

    for field in REQUIRED_DEPRECATION_FIELDS:
        value = entry.get(field)
        if value in (None, ""):
            raise DeprecationPolicyError(f"missing required field: {field}")

    dep_date = parse_iso_date(str(entry["deprecation_date"]), field_name="deprecation_date")
    rem_date = parse_iso_date(str(entry["removal_date"]), field_name="removal_date")

    migration_path = str(entry["migration_path"]).strip()
    if not migration_path:
        raise DeprecationPolicyError("migration_path must be a non-empty string.")

    validate_notice_window(
        dep_date,
        rem_date,
        minimum_notice_days=minimum_notice_days,
    )


def validate_deprecation_registry(
    registry: Mapping[str, Any],
    *,
    minimum_notice_days: int = DEFAULT_MINIMUM_NOTICE_DAYS,
) -> None:
    """Validate deprecation metadata for versions and endpoints registry."""

    policy = registry.get("policy", {})
    if isinstance(policy, Mapping):
        configured_days = policy.get("minimum_notice_days")
        if isinstance(configured_days, int):
            minimum_notice_days = configured_days

    for group_name in ("versions", "endpoints"):
        entries = registry.get(group_name, [])
        if entries is None:
            continue
        if not isinstance(entries, list):
            raise DeprecationPolicyError(f"{group_name} must be a list.")

        for entry in entries:
            if not isinstance(entry, Mapping):
                raise DeprecationPolicyError(
                    f"{group_name} entries must be mapping objects."
                )
            if _requires_validation(entry):
                validate_deprecation_entry(
                    entry,
                    minimum_notice_days=minimum_notice_days,
                )


def load_deprecation_registry(path: str | Path) -> dict[str, Any]:
    """Load and parse a YAML deprecation registry file."""

    registry_path = Path(path)
    with registry_path.open("r", encoding="utf-8") as file:
        raw_data = yaml.safe_load(file) or {}

    if not isinstance(raw_data, dict):
        raise DeprecationPolicyError("Deprecation registry root must be a mapping.")

    return raw_data


def validate_deprecation_registry_file(path: str | Path) -> None:
    """Load and validate deprecation registry file in one step."""

    registry = load_deprecation_registry(path)
    validate_deprecation_registry(registry)


def load_and_validate_deprecation_registry(
    path: str | Path = DEFAULT_DEPRECATION_REGISTRY_PATH,
) -> dict[str, Any]:
    """Load and validate deprecation registry, returning parsed mapping."""

    registry = load_deprecation_registry(path)
    validate_deprecation_registry(registry)
    return registry
