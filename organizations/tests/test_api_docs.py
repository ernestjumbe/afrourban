"""Schema and documentation tests for organizations."""

from __future__ import annotations

import yaml
import pytest
from rest_framework.test import APIClient

from users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db

ORGANIZATION_EXPECTED_OPERATIONS: dict[str, set[str]] = {
    "/api/v1/organizations/": {"get", "post"},
    "/api/v1/organizations/{organization_id}/": {"get", "patch"},
    "/api/v1/organizations/{organization_id}/logo/": {"post", "delete"},
    "/api/v1/organizations/{organization_id}/cover/": {"post", "delete"},
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


def test_internal_schema_includes_organization_routes():
    """Internal schema should publish all organizations operations."""

    client = APIClient()
    client.force_authenticate(user=UserFactory())

    response = client.get("/api/v1/docs/internal/schema/")
    assert response.status_code == 200

    schema = _load_schema(response)

    for path, expected_methods in ORGANIZATION_EXPECTED_OPERATIONS.items():
        assert path in schema["paths"]
        assert _operation_methods(schema, path) == expected_methods
        for operation in schema["paths"][path].values():
            assert operation.get("x-access-scope") == "authenticated"


def test_public_schema_excludes_organization_routes():
    """Public schema should not expose authenticated organizations endpoints."""

    client = APIClient()
    response = client.get("/api/v1/docs/public/schema/")
    assert response.status_code == 200

    schema = _load_schema(response)

    for path in ORGANIZATION_EXPECTED_OPERATIONS:
        assert path not in schema["paths"]
