"""Health service layer."""

from __future__ import annotations

from dataclasses import dataclass
from http import HTTPStatus
from typing import Literal

import structlog

HealthPhase = Literal["starting", "running", "stopping", "failing"]
HealthStatus = Literal["healthy", "unhealthy"]
HealthScope = Literal["application_process_only"]

APPLICATION_PROCESS_ONLY_SCOPE: HealthScope = "application_process_only"

logger = structlog.get_logger(__name__)


@dataclass(frozen=True, slots=True)
class HealthCheckResult:
    """Result of evaluating application-process health."""

    phase: HealthPhase
    can_handle_requests_normally: bool
    status: HealthStatus
    http_status: HTTPStatus
    dependency_status_ignored: bool = True

    @classmethod
    def healthy(cls) -> "HealthCheckResult":
        """Return the canonical healthy result."""

        return cls(
            phase="running",
            can_handle_requests_normally=True,
            status="healthy",
            http_status=HTTPStatus.OK,
        )

    @classmethod
    def unhealthy(cls, *, phase: HealthPhase) -> "HealthCheckResult":
        """Return the canonical unhealthy result for a non-running phase."""

        return cls(
            phase=phase,
            can_handle_requests_normally=False,
            status="unhealthy",
            http_status=HTTPStatus.SERVICE_UNAVAILABLE,
        )


def evaluate_application_health(
    *,
    phase: HealthPhase = "running",
    can_handle_requests_normally: bool = True,
    dependencies_healthy: bool | None = None,
) -> HealthCheckResult:
    """Evaluate application-process health without checking external dependencies.

    `dependencies_healthy` is accepted only to make the contract explicit in tests and
    future call sites. It is intentionally ignored so dependency outages alone cannot
    flip the health result.
    """

    if phase != "running" or not can_handle_requests_normally:
        return HealthCheckResult.unhealthy(phase=phase)

    return HealthCheckResult.healthy()


def log_health_check_evaluated(
    *,
    result: HealthCheckResult,
    method: str,
    path: str,
    request_user_id: int | None,
) -> None:
    """Emit the structured observability event for a health-check evaluation."""

    logger.info(
        "health_check_evaluated",
        outcome=result.status,
        http_status=result.http_status,
        method=method,
        path=path,
        request_user_id=request_user_id,
        scope=APPLICATION_PROCESS_ONLY_SCOPE,
    )
