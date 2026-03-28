"""Tests for public/internal API documentation visibility and coverage."""

from __future__ import annotations

import yaml
import pytest
from rest_framework.test import APIClient

from users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


INTERNAL_EXPECTED_OPERATIONS: dict[str, set[str]] = {
    "/api/v1/auth/register/": {"post"},
    "/api/v1/auth/token/": {"post"},
    "/api/v1/auth/token/refresh/": {"post"},
    "/api/v1/auth/token/verify/": {"post"},
    "/api/v1/auth/email-verification/verify/": {"post"},
    "/api/v1/auth/email-verification/resend/": {"post"},
    "/api/v1/auth/password/reset/": {"post"},
    "/api/v1/auth/password/reset/confirm/": {"post"},
    "/api/v1/auth/passkey/register/options/": {"post"},
    "/api/v1/auth/passkey/register/complete/": {"post"},
    "/api/v1/auth/passkey/authenticate/options/": {"post"},
    "/api/v1/auth/passkey/authenticate/complete/": {"post"},
    "/api/v1/auth/logout/": {"post"},
    "/api/v1/auth/password/change/": {"post"},
    "/api/v1/auth/passkey/add/options/": {"post"},
    "/api/v1/auth/passkey/add/complete/": {"post"},
    "/api/v1/auth/passkey/": {"get"},
    "/api/v1/auth/passkey/{credential_id}/": {"delete"},
    "/api/v1/profiles/me/": {"get", "patch"},
    "/api/v1/profiles/me/avatar/": {"post", "delete"},
    "/api/v1/profiles/policies/{policy_id}/check/": {"get"},
    "/api/v1/profiles/{user_id}/": {"get"},
    "/api/v1/admin/users/": {"get"},
    "/api/v1/admin/users/{user_id}/": {"get", "patch"},
    "/api/v1/admin/users/{user_id}/activate/": {"post"},
    "/api/v1/admin/users/{user_id}/deactivate/": {"post"},
    "/api/v1/admin/users/{user_id}/permissions/": {"get", "put"},
    "/api/v1/admin/users/roles/": {"get", "post"},
    "/api/v1/admin/users/roles/{role_id}/": {"get", "patch", "delete"},
}


def _operation_methods(schema: dict, path: str) -> set[str]:
    operations = schema["paths"].get(path, {})
    return {method for method in operations.keys() if method in {"get", "post", "put", "patch", "delete"}}


def _load_schema(response) -> dict:
    return yaml.safe_load(response.content.decode("utf-8"))


def test_internal_schema_includes_complete_contract_inventory():
    """Internal schema must include every active endpoint from the contract."""

    user = UserFactory()
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/v1/docs/internal/schema/")
    assert response.status_code == 200

    schema = _load_schema(response)
    assert "paths" in schema

    for path, expected_methods in INTERNAL_EXPECTED_OPERATIONS.items():
        assert path in schema["paths"]
        assert _operation_methods(schema, path) == expected_methods


def test_internal_docs_and_schema_access_control():
    """Public docs are open; internal docs and schema require authentication."""

    anonymous = APIClient()

    public_docs = anonymous.get("/api/v1/docs/public/")
    public_schema = anonymous.get("/api/v1/docs/public/schema/")
    assert public_docs.status_code == 200
    assert public_schema.status_code == 200

    internal_docs = anonymous.get("/api/v1/docs/internal/")
    internal_schema = anonymous.get("/api/v1/docs/internal/schema/")
    assert internal_docs.status_code in {401, 403}
    assert internal_schema.status_code in {401, 403}

    authenticated = APIClient()
    authenticated.force_authenticate(user=UserFactory())
    auth_internal_docs = authenticated.get("/api/v1/docs/internal/")
    auth_internal_schema = authenticated.get("/api/v1/docs/internal/schema/")
    assert auth_internal_docs.status_code == 200
    assert auth_internal_schema.status_code == 200


def test_internal_schema_includes_deprecation_metadata():
    """Internal schema must expose deprecation policy metadata."""

    client = APIClient()
    client.force_authenticate(user=UserFactory())

    response = client.get("/api/v1/docs/internal/schema/")
    assert response.status_code == 200

    schema = _load_schema(response)
    metadata = schema.get("x-deprecations")
    assert isinstance(metadata, dict)
    assert metadata["minimum_notice_days"] >= 90
    assert {
        "deprecation_date",
        "removal_date",
        "migration_path",
    }.issubset(set(metadata["required_fields"]))
    assert "versions" in metadata
    assert "endpoints" in metadata
