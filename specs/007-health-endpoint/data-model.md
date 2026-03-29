# Data Model: Application Health Endpoint

**Feature**: 007-health-endpoint  
**Date**: 2026-03-29

This feature does not introduce database tables. The entities below are conceptual runtime and
contract entities used by the endpoint, schema, and tests.

## Entity: ApplicationHealthStatus

Represents the availability result returned by `GET /api/v1/health/`.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `status` | enum | required (`healthy`, `unhealthy`) | Single machine-readable response field |
| `http_status` | enum | required (`200`, `503`) | HTTP status code paired with `status` |
| `scope` | enum | required (`application_process_only`) | Declares that only application-process health is evaluated |
| `rate_limited` | boolean | fixed `false` | Captures the contract that health checks are not throttled |

### Validation Rules

- `status=healthy` MUST map to HTTP `200`.
- `status=unhealthy` MUST map to HTTP `503`.
- Response payload MUST contain only the `status` field.
- `scope` MUST remain `application_process_only`; dependency status cannot influence the result.

### State Transitions

```text
healthy <-> unhealthy
```

- `healthy -> unhealthy`: occurs when the application cannot handle requests normally, including
  startup, shutdown, or internal evaluation failure.
- `unhealthy -> healthy`: occurs when the application can resume normal request handling.

## Entity: HealthCheckRequest

Represents an incoming request made by a monitoring system, frontend application, or other caller.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `method` | enum | fixed `GET` | Only supported operation |
| `path` | string | fixed `/api/v1/health/` | Canonical endpoint path |
| `authentication_required` | boolean | fixed `false` | Anonymous access contract |
| `credentials_present` | boolean | optional | Whether caller sent auth material anyway |
| `caller_type` | enum | optional (`monitoring`, `frontend`, `other`) | Conceptual consumer type |

### Validation Rules

- Request MUST be accepted without authentication.
- Presence of credentials MUST NOT change the returned health result.
- Request MUST bypass throttling logic.

## Entity: ApplicationLifecycleSnapshot

Represents the runtime condition used to derive the health result.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `phase` | enum | required (`starting`, `running`, `stopping`, `failing`) | Current application lifecycle phase |
| `can_handle_requests_normally` | boolean | required | Whether the app can serve requests successfully |
| `dependency_status_ignored` | boolean | fixed `true` | Confirms external dependency health is not evaluated |

### Validation Rules

- `phase=running` and `can_handle_requests_normally=true` yields `ApplicationHealthStatus.status=healthy`.
- `phase=starting` or `phase=stopping` yields `ApplicationHealthStatus.status=unhealthy`.
- Any evaluation failure yields `ApplicationHealthStatus.status=unhealthy`.
- External dependency state MUST NOT change the derived status.
