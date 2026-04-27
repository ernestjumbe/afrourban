"""Versioned routing tests for organizations."""

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
        ("GET", "/api/v1/organizations/"),
        ("POST", "/api/v1/organizations/"),
        ("GET", "/api/v1/organizations/1/"),
        ("PATCH", "/api/v1/organizations/1/"),
        ("POST", "/api/v1/organizations/1/logo/"),
        ("DELETE", "/api/v1/organizations/1/logo/"),
        ("POST", "/api/v1/organizations/1/cover/"),
        ("DELETE", "/api/v1/organizations/1/cover/"),
    ],
)
def test_organization_api_v1_routes_are_registered(method: str, path: str):
    """Every organizations endpoint should resolve under /api/v1/."""

    client = APIClient()
    response = _call(client, method, path)
    assert response.status_code not in {404, 405}


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/api/organizations/"),
        ("POST", "/api/organizations/"),
        ("GET", "/api/organizations/1/"),
        ("PATCH", "/api/organizations/1/"),
    ],
)
def test_legacy_unversioned_organization_routes_are_rejected(method: str, path: str):
    """Organizations are available only through the versioned API namespace."""

    client = APIClient()
    response = _call(client, method, path)
    assert response.status_code == 404
