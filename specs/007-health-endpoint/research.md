# Research: Application Health Endpoint

**Feature**: 007-health-endpoint  
**Date**: 2026-03-29

## 1. Django App Placement

### Decision

Implement the feature as a dedicated `health` Django app and add it to `INSTALLED_APPS`. The app
will include the constitution-required layout (`models.py`, `selectors.py`, `services.py`,
`urls.py`, `views.py`) plus a dedicated output serializer and focused tests.

### Rationale

The endpoint is operational infrastructure, not user or profile domain logic. A small dedicated app
keeps concerns isolated and stays consistent with the project's styleguide requirements for new
Django apps.

### Alternatives considered

- Add a one-off view directly in `afrourban/urls.py`: rejected because it bypasses the app layout
  enforced by the constitution.
- Add the endpoint to `users` or `profiles`: rejected because health signaling is unrelated to
  either domain and would create an artificial coupling.

## 2. Health Evaluation Boundary

### Decision

The health evaluation will check only whether the Django application process can handle requests
normally. It will not perform database pings, cache checks, third-party API calls, or any other
external dependency validation. Startup, shutdown, or internal evaluation failure will yield a
non-healthy result.

### Rationale

This exactly matches the approved feature scope and keeps the endpoint fast, deterministic, and
stable for monitoring and frontend availability checks.

### Alternatives considered

- Include database or cache checks: rejected because the specification explicitly excludes external
  dependency verification.
- Add detailed readiness diagnostics: rejected because the endpoint is intentionally scoped to a
  simple availability signal, not a comprehensive ops dashboard.

## 3. Endpoint Response Contract

### Decision

Expose `GET /api/v1/health/` with:

- `AllowAny` access
- explicit no-throttle behavior
- HTTP `200` with `{"status": "healthy"}` when the app can handle requests normally
- HTTP `503` with `{"status": "unhealthy"}` when it cannot

The response body will contain only the `status` field in both cases.

### Rationale

The clarified contract favors an invariant machine-readable shape that is easy for uptime monitors
and frontend bootstrap logic to parse without special-case handling.

### Alternatives considered

- Always return `200`: rejected by clarification because callers need an HTTP-level non-healthy
  signal.
- Include timestamps or scope text in the body: rejected by clarification because only one status
  field is allowed.
- Return RFC 9457 Problem Details for `503`: rejected because it breaks the approved single-field
  response contract.

## 4. Routing and Documentation Visibility

### Decision

Register the endpoint through `health.urls.api_v1_urlpatterns` and include it from
`afrourban/urls.py` under `/api/`, yielding `/api/v1/health/`. Update `afrourban/api_schema.py` so
`/api/v1/health/` is classified as a public endpoint and therefore appears in both public and
internal schema views. Regenerate committed OpenAPI artifacts after implementation.

### Rationale

This preserves the repo's existing API registration model and ensures monitoring/frontends can
discover the endpoint through the same published docs pipeline as other public API surfaces.

### Alternatives considered

- Leave the endpoint out of OpenAPI: rejected because the spec requires published API documentation.
- Publish it only in internal docs: rejected because the endpoint is intentionally public and meant
  for anonymous consumers.

## 5. Observability Strategy

### Decision

Emit a structured log event for each health evaluation, for example `health_check_evaluated`, with
fields such as:

- `outcome` (`healthy` or `unhealthy`)
- `http_status`
- `method`
- `path`
- `request_user_id` (nullable/anonymous)

No dependency details, secrets, or verbose diagnostics will be logged.

### Rationale

This satisfies the constitution's structured observability requirement while keeping the endpoint's
scope intentionally minimal.

### Alternatives considered

- No dedicated logging: rejected because the feature is operationally important and needs a clear
  audit signal.
- Log dependency-level diagnostics: rejected because dependency health is out of scope and would
  increase noise and leakage risk.

## 6. Test Strategy

### Decision

Use test-first coverage across three layers:

1. Unit tests for health evaluation service behavior
2. API integration/contract tests for anonymous access, `200`/`503` semantics, single-field body,
   and startup/shutdown behavior
3. Schema/documentation tests proving the endpoint appears in public and internal OpenAPI output

Where rate-limiting exemption cannot be observed through current global settings, assert the view's
explicit no-throttle configuration as a contract safeguard.

### Rationale

This matches the constitution and directly validates the feature's behavioral contract instead of
only checking implementation details.

### Alternatives considered

- API tests only: rejected because service behavior and lifecycle transitions would be harder to
  validate precisely.
- Manual schema verification only: rejected because public/internal doc drift is easy to regress.
