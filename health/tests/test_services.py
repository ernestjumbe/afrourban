"""Tests for health service behavior."""

from http import HTTPStatus

import pytest

from health.services import (
    evaluate_application_health,
    log_health_check_evaluated,
)


class TestEvaluateApplicationHealth:
    """Application health evaluation should reflect only process lifecycle."""

    def test_returns_healthy_for_running_process(self):
        result = evaluate_application_health()

        assert result.status == "healthy"
        assert result.http_status == HTTPStatus.OK
        assert result.phase == "running"

    def test_returns_unhealthy_for_starting_process(self):
        result = evaluate_application_health(
            phase="starting",
            can_handle_requests_normally=False,
        )

        assert result.status == "unhealthy"
        assert result.http_status == HTTPStatus.SERVICE_UNAVAILABLE
        assert result.phase == "starting"

    def test_returns_unhealthy_for_stopping_process(self):
        result = evaluate_application_health(
            phase="stopping",
            can_handle_requests_normally=False,
        )

        assert result.status == "unhealthy"
        assert result.http_status == HTTPStatus.SERVICE_UNAVAILABLE
        assert result.phase == "stopping"

    def test_returns_unhealthy_when_requests_cannot_be_handled_normally(self):
        result = evaluate_application_health(
            phase="running",
            can_handle_requests_normally=False,
        )

        assert result.status == "unhealthy"
        assert result.http_status == HTTPStatus.SERVICE_UNAVAILABLE
        assert result.phase == "running"

    @pytest.mark.parametrize("dependencies_healthy", [True, False])
    def test_ignores_external_dependency_health_for_running_process(
        self,
        dependencies_healthy: bool,
    ):
        result = evaluate_application_health(
            phase="running",
            can_handle_requests_normally=True,
            dependencies_healthy=dependencies_healthy,
        )

        assert result.status == "healthy"
        assert result.http_status == HTTPStatus.OK
        assert result.dependency_status_ignored is True


class TestLogHealthCheckEvaluated:
    """Structured logging for health evaluation should stay minimal."""

    def test_logs_single_structured_health_evaluation_event(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ):
        events: list[tuple[str, dict[str, object]]] = []

        def capture(event: str, **kwargs: object) -> None:
            events.append((event, kwargs))

        monkeypatch.setattr("health.services.logger.info", capture)
        result = evaluate_application_health(
            dependencies_healthy=False,
        )

        log_health_check_evaluated(
            result=result,
            method="GET",
            path="/api/v1/health/",
            request_user_id=None,
        )

        assert events == [
            (
                "health_check_evaluated",
                {
                    "outcome": "healthy",
                    "http_status": HTTPStatus.OK,
                    "method": "GET",
                    "path": "/api/v1/health/",
                    "request_user_id": None,
                    "scope": "application_process_only",
                },
            )
        ]
