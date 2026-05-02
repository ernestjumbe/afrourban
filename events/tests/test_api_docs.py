"""Schema and documentation tests for events."""

from __future__ import annotations

import yaml
import pytest
from rest_framework.test import APIClient

from users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db

EVENT_EXPECTED_OPERATIONS: dict[str, set[str]] = {
    "/api/v1/events/": {"post"},
    "/api/v1/events/{event_id}/": {"get", "patch"},
    "/api/v1/events/{event_id}/cover/": {"post", "delete"},
}


def _operation_methods(schema: dict, path: str) -> set[str]:
    operations = schema["paths"].get(path, {})
    return {
        method
        for method in operations.keys()
        if method in {"get", "post", "put", "patch", "delete"}
    }


def _load_schema(response) -> dict:
    return yaml.safe_load(response.content.decode("utf-8"))


def test_internal_schema_includes_event_routes():
    """Internal schema should publish all authenticated event operations."""

    client = APIClient()
    client.force_authenticate(user=UserFactory())

    response = client.get("/api/v1/docs/internal/schema/")
    assert response.status_code == 200

    schema = _load_schema(response)

    for path, expected_methods in EVENT_EXPECTED_OPERATIONS.items():
        assert path in schema["paths"]
        assert _operation_methods(schema, path) == expected_methods
        for operation in schema["paths"][path].values():
            assert operation.get("x-access-scope") == "authenticated"


def test_public_schema_excludes_event_routes():
    """Public schema should not expose authenticated events endpoints."""

    client = APIClient()
    response = client.get("/api/v1/docs/public/schema/")
    assert response.status_code == 200

    schema = _load_schema(response)

    for path in EVENT_EXPECTED_OPERATIONS:
        assert path not in schema["paths"]
