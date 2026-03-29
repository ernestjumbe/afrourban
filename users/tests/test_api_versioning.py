"""Contract tests for API versioned routing under /api/v1/."""

import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def _call(client: APIClient, method: str, path: str):
    method = method.upper()
    if method == "GET":
        return client.get(path)
    if method == "POST":
        return client.post(path, {}, format="json")
    if method == "PUT":
        return client.put(path, {}, format="json")
    if method == "PATCH":
        return client.patch(path, {}, format="json")
    if method == "DELETE":
        return client.delete(path)
    raise ValueError(f"Unsupported method: {method}")


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("POST", "/api/v1/auth/register/"),
        ("POST", "/api/v1/auth/token/"),
        ("POST", "/api/v1/auth/token/refresh/"),
        ("POST", "/api/v1/auth/token/verify/"),
        ("POST", "/api/v1/auth/logout/"),
        ("PATCH", "/api/v1/auth/username/"),
        ("POST", "/api/v1/auth/email-verification/verify/"),
        ("POST", "/api/v1/auth/email-verification/resend/"),
        ("POST", "/api/v1/auth/password/reset/"),
        ("POST", "/api/v1/auth/password/reset/confirm/"),
        ("POST", "/api/v1/auth/password/change/"),
        ("POST", "/api/v1/auth/passkey/register/options/"),
        ("POST", "/api/v1/auth/passkey/register/complete/"),
        ("POST", "/api/v1/auth/passkey/authenticate/options/"),
        ("POST", "/api/v1/auth/passkey/authenticate/complete/"),
        ("POST", "/api/v1/auth/passkey/add/options/"),
        ("POST", "/api/v1/auth/passkey/add/complete/"),
        ("GET", "/api/v1/auth/passkey/"),
        ("DELETE", "/api/v1/auth/passkey/1/"),
        ("GET", "/api/v1/admin/users/"),
        ("GET", "/api/v1/admin/users/1/"),
        ("PATCH", "/api/v1/admin/users/1/"),
        ("POST", "/api/v1/admin/users/1/activate/"),
        ("POST", "/api/v1/admin/users/1/deactivate/"),
        ("GET", "/api/v1/admin/users/1/permissions/"),
        ("PUT", "/api/v1/admin/users/1/permissions/"),
        ("GET", "/api/v1/admin/users/roles/"),
        ("POST", "/api/v1/admin/users/roles/"),
        ("GET", "/api/v1/admin/users/roles/1/"),
        ("PATCH", "/api/v1/admin/users/roles/1/"),
        ("DELETE", "/api/v1/admin/users/roles/1/"),
    ],
)
def test_users_and_admin_api_v1_routes_are_registered(method: str, path: str):
    """Every contract-listed users/admin endpoint resolves under /api/v1/."""

    client = APIClient()
    response = _call(client, method, path)
    assert response.status_code not in {404, 405}


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("POST", "/api/auth/register/"),
        ("POST", "/api/auth/token/"),
        ("POST", "/api/auth/logout/"),
        ("GET", "/api/admin/users/"),
        ("GET", "/api/admin/users/1/"),
        ("GET", "/api/profiles/me/"),
        ("GET", "/api/profiles/1/"),
    ],
)
def test_legacy_unversioned_routes_are_rejected(method: str, path: str):
    """Legacy unversioned APIs are removed once /api/v1/ is canonical."""

    client = APIClient()
    response = _call(client, method, path)
    assert response.status_code == 404
