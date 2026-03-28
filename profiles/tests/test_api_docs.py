"""Tests for profile endpoint documentation visibility filtering."""

from __future__ import annotations

import yaml
import pytest
from rest_framework.test import APIClient

PUBLIC_EXPECTED_OPERATIONS: dict[str, set[str]] = {
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
}

INTERNAL_ONLY_PATHS = {
    "/api/v1/auth/logout/",
    "/api/v1/auth/password/change/",
    "/api/v1/auth/passkey/add/options/",
    "/api/v1/auth/passkey/add/complete/",
    "/api/v1/auth/passkey/",
    "/api/v1/auth/passkey/{credential_id}/",
    "/api/v1/profiles/me/",
    "/api/v1/profiles/me/avatar/",
    "/api/v1/profiles/policies/{policy_id}/check/",
    "/api/v1/profiles/{user_id}/",
    "/api/v1/admin/users/",
    "/api/v1/admin/users/{user_id}/",
    "/api/v1/admin/users/{user_id}/activate/",
    "/api/v1/admin/users/{user_id}/deactivate/",
    "/api/v1/admin/users/{user_id}/permissions/",
    "/api/v1/admin/users/roles/",
    "/api/v1/admin/users/roles/{role_id}/",
}

pytestmark = pytest.mark.django_db


def _operation_methods(schema: dict, path: str) -> set[str]:
    operations = schema["paths"].get(path, {})
    return {method for method in operations.keys() if method in {"get", "post", "put", "patch", "delete"}}


def _load_schema(response) -> dict:
    return yaml.safe_load(response.content.decode("utf-8"))


def test_public_schema_filters_out_authenticated_and_staff_paths():
    """Public schema must include only public endpoints."""

    client = APIClient()
    response = client.get("/api/v1/docs/public/schema/")
    assert response.status_code == 200

    schema = _load_schema(response)
    assert "paths" in schema

    for path, expected_methods in PUBLIC_EXPECTED_OPERATIONS.items():
        assert path in schema["paths"]
        assert _operation_methods(schema, path) == expected_methods

        for operation in schema["paths"][path].values():
            assert operation.get("x-access-scope") == "public"

    for internal_path in INTERNAL_ONLY_PATHS:
        assert internal_path not in schema["paths"]
