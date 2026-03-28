"""Contract tests for profile API versioned routing under /api/v1/."""

import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def _call(client: APIClient, method: str, path: str):
    method = method.upper()
    if method == "GET":
        return client.get(path)
    if method == "POST":
        return client.post(path, {}, format="json")
    if method == "PATCH":
        return client.patch(path, {}, format="json")
    if method == "DELETE":
        return client.delete(path)
    raise ValueError(f"Unsupported method: {method}")


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/api/v1/profiles/me/"),
        ("PATCH", "/api/v1/profiles/me/"),
        ("POST", "/api/v1/profiles/me/avatar/"),
        ("DELETE", "/api/v1/profiles/me/avatar/"),
        ("GET", "/api/v1/profiles/policies/1/check/"),
        ("GET", "/api/v1/profiles/1/"),
    ],
)
def test_profile_api_v1_routes_are_registered(method: str, path: str):
    """Every contract-listed profile endpoint resolves under /api/v1/."""

    client = APIClient()
    response = _call(client, method, path)
    assert response.status_code not in {404, 405}
