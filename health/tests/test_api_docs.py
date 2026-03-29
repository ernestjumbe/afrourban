"""Schema and documentation tests for the health endpoint."""

from __future__ import annotations

import yaml
import pytest
from rest_framework.test import APIClient

from users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db

HEALTH_PATH = "/api/v1/health/"


def _load_schema(response) -> dict:
    return yaml.safe_load(response.content.decode("utf-8"))


def test_health_endpoint_appears_in_public_and_internal_schema():
    public_client = APIClient()
    public_response = public_client.get("/api/v1/docs/public/schema/")
    assert public_response.status_code == 200

    public_schema = _load_schema(public_response)
    public_operation = public_schema["paths"][HEALTH_PATH]["get"]
    assert public_operation["x-access-scope"] == "public"

    internal_client = APIClient()
    internal_client.force_authenticate(user=UserFactory())
    internal_response = internal_client.get("/api/v1/docs/internal/schema/")
    assert internal_response.status_code == 200

    internal_schema = _load_schema(internal_response)
    internal_operation = internal_schema["paths"][HEALTH_PATH]["get"]
    assert internal_operation["x-access-scope"] == "public"


def test_health_endpoint_schema_documents_anonymous_status_contract():
    client = APIClient()

    response = client.get("/api/v1/docs/public/schema/")
    assert response.status_code == 200

    schema = _load_schema(response)
    operation = schema["paths"][HEALTH_PATH]["get"]

    assert operation["summary"] == "Application health check"
    assert "frontend" in operation["description"].lower()
    assert "application-process" in operation["description"].lower()
    assert set(operation["responses"]) >= {"200", "503"}
    assert operation["security"] == [{}]
