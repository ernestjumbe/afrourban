"""API contract tests for the health endpoint."""

from __future__ import annotations

from http import HTTPStatus
from typing import cast

from django.urls import resolve
import pytest
from rest_framework.test import APIClient

from health.services import (
    HealthCheckResult,
    HealthPhase,
    HealthStatus,
    evaluate_application_health,
)
from health.views import HealthView
from users.tests.factories import UserFactory


def _mock_result(
    *,
    phase: HealthPhase,
    status: HealthStatus,
    http_status: HTTPStatus,
) -> HealthCheckResult:
    return HealthCheckResult(
        phase=phase,
        can_handle_requests_normally=(status == "healthy"),
        status=status,
        http_status=http_status,
    )


def test_health_endpoint_allows_anonymous_access_and_returns_healthy_status():
    client = APIClient()

    response = client.get("/api/v1/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.django_db
def test_health_endpoint_returns_same_healthy_result_with_credentials_present():
    anonymous_client = APIClient()
    authenticated_client = APIClient()
    authenticated_client.force_authenticate(user=UserFactory())

    anonymous_response = anonymous_client.get("/api/v1/health/")
    authenticated_response = authenticated_client.get("/api/v1/health/")

    assert anonymous_response.status_code == 200
    assert authenticated_response.status_code == 200
    assert anonymous_response.json() == {"status": "healthy"}
    assert authenticated_response.json() == anonymous_response.json()


@pytest.mark.parametrize(
    ("phase", "expected_status_code"),
    [
        ("starting", 503),
        ("stopping", 503),
    ],
)
def test_health_endpoint_returns_unhealthy_for_non_running_lifecycle_states(
    monkeypatch: pytest.MonkeyPatch,
    phase: str,
    expected_status_code: int,
):
    monkeypatch.setattr(
        "health.views.evaluate_application_health",
        lambda: _mock_result(
            phase=cast(HealthPhase, phase),
            status="unhealthy",
            http_status=HTTPStatus(expected_status_code),
        ),
    )
    client = APIClient()

    response = client.get("/api/v1/health/")

    assert response.status_code == expected_status_code
    assert response.json() == {"status": "unhealthy"}


def test_health_endpoint_returns_unhealthy_when_evaluation_fails(
    monkeypatch: pytest.MonkeyPatch,
):
    def raise_failure() -> None:
        raise RuntimeError("unexpected health evaluation failure")

    monkeypatch.setattr("health.views.evaluate_application_health", raise_failure)
    client = APIClient()

    response = client.get("/api/v1/health/")

    assert response.status_code == 503
    assert response.json() == {"status": "unhealthy"}


def test_health_endpoint_is_explicitly_exempt_from_throttling():
    resolved = resolve("/api/v1/health/")

    assert resolved.func.view_class is HealthView
    assert HealthView.throttle_classes == []


def test_health_endpoint_ignores_dependency_failures_and_stays_status_only(
    monkeypatch: pytest.MonkeyPatch,
):
    logged_calls: list[dict[str, object]] = []

    monkeypatch.setattr(
        "health.views.evaluate_application_health",
        lambda: evaluate_application_health(dependencies_healthy=False),
    )
    monkeypatch.setattr(
        "health.views.log_health_check_evaluated",
        lambda **kwargs: logged_calls.append(kwargs),
    )
    client = APIClient()

    response = client.get("/api/v1/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
    assert set(response.json()) == {"status"}
    assert len(logged_calls) == 1
    assert logged_calls[0]["method"] == "GET"
    assert logged_calls[0]["path"] == "/api/v1/health/"
    assert logged_calls[0]["request_user_id"] is None


def test_health_endpoint_never_exposes_dependency_diagnostics_in_error_responses(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(
        "health.views.evaluate_application_health",
        lambda: _mock_result(
            phase="failing",
            status="unhealthy",
            http_status=HTTPStatus.SERVICE_UNAVAILABLE,
        ),
    )
    monkeypatch.setattr(
        "health.views.log_health_check_evaluated",
        lambda **kwargs: None,
    )
    client = APIClient()

    response = client.get("/api/v1/health/")

    assert response.status_code == 503
    assert response.json() == {"status": "unhealthy"}
    assert set(response.json()) == {"status"}
    assert "phase" not in response.json()
    assert "dependencies_healthy" not in response.json()
    assert "dependency_diagnostics" not in response.json()
