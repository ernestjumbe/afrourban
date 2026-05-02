"""Versioned routing tests for events."""

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
        ("POST", "/api/v1/events/"),
        ("GET", "/api/v1/events/1/"),
        ("PATCH", "/api/v1/events/1/"),
        ("POST", "/api/v1/events/1/cover/"),
        ("DELETE", "/api/v1/events/1/cover/"),
    ],
)
def test_event_api_v1_routes_are_registered(method: str, path: str):
    """Every events endpoint should resolve under /api/v1/."""

    client = APIClient()
    response = _call(client, method, path)
    assert response.status_code not in {404, 405}


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("POST", "/api/events/"),
        ("GET", "/api/events/1/"),
        ("PATCH", "/api/events/1/"),
        ("POST", "/api/events/1/cover/"),
        ("DELETE", "/api/events/1/cover/"),
    ],
)
def test_legacy_unversioned_event_routes_are_rejected(method: str, path: str):
    """Events are available only through the versioned API namespace."""

    client = APIClient()
    response = _call(client, method, path)
    assert response.status_code == 404
