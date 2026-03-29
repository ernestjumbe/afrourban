# Implementation Plan: Application Health Endpoint

**Branch**: `007-health-endpoint` | **Date**: 2026-03-29 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/007-health-endpoint/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add a dedicated `health` Django app that exposes a public `GET /api/v1/health/` endpoint for
monitoring systems and frontend startup checks. The endpoint will return only a machine-readable
`status` field, use HTTP `200` when healthy and HTTP `503` when non-healthy, stay unauthenticated
and unthrottled, report only application-process health, appear in both public and internal OpenAPI
documentation, and emit structured observability events for each evaluation.

## Technical Context

**Language/Version**: Python 3.11 (project constraint `^3.11`)  
**Primary Dependencies**: Django 5.1.2, Django REST Framework 3.17.1, drf-spectacular 0.29.0, structlog, SimpleJWT (existing project auth stack)  
**Storage**: Existing PostgreSQL (production) / SQLite (dev+test); no new persistent tables or migrations required  
**Testing**: pytest + pytest-django; unit tests for health evaluation logic and integration/contract tests for API and schema behavior  
**Target Platform**: Linux containerized web service (Docker/Gunicorn), local macOS development  
**Project Type**: Django REST API service  
**Performance Goals**: Meet spec target of 95% of health requests completing in under 1 second during normal operation; avoid database and external network calls in the health path  
**Constraints**: Endpoint must be mounted at `/api/v1/health/`, allow anonymous access, return only `{"status": "<healthy|unhealthy>"}`, use `200`/`503`, ignore external dependency health, remain exempt from rate limiting, and report non-healthy during startup/shutdown until normal request handling is available  
**Scale/Scope**: One new public endpoint, one new lightweight Django app, schema visibility updates, committed documentation artifacts, and focused automated coverage

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. HackSoftware Styleguide | PASS | New `health` app will keep evaluation in `services.py`, use a dedicated output serializer, and keep `APIView` orchestration thin |
| II. API-First Design | PASS | Endpoint stays under `/api/v1/`, is registered via `api_urlpatterns`, and is published in drf-spectacular docs; the status-only `503` body is a documented contract exception tracked in Complexity Tracking |
| III. Test-First Development | PASS | Plan starts with failing service, API, and schema tests before implementation |
| IV. Code Quality | PASS | Plan includes `poetry run ruff check .`, `poetry run mypy .`, `poetry run pytest`, and `poetry run python manage.py spectacular --file ... --validate` |
| V. Structured Observability | PASS | Health evaluations will emit structured logs with outcome, HTTP status, method, path, and anonymous/user context |
| VI. Simplicity & Reuse | PASS | Uses a small dedicated app plus existing DRF/schema infrastructure; avoids dependency probes and extra persistence |
| VII. Poetry-Managed Toolchain | PASS | All implementation and validation commands remain Poetry-managed |

**Pre-Phase 0 gate: PASS** — no blocking constitution issues; one deliberate response-envelope exception is documented below.

## Phase 0 Research Summary

Research decisions are captured in [research.md](research.md), covering:

1. Dedicated `health` app placement and file layout
2. Application-process-only evaluation boundary
3. Stable response contract (`200`/`503` plus single `status` field)
4. Public OpenAPI visibility and route-registration strategy
5. Explicit no-throttle/anonymous-access behavior
6. Structured logging and automated test strategy

## Project Structure

### Documentation (this feature)

```text
specs/007-health-endpoint/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── health-endpoint.md
└── tasks.md
```

### Source Code (repository root)

```text
afrourban/
├── urls.py                         # register health URLs via api_urlpatterns under /api/
├── api_schema.py                   # classify /api/v1/health/ as public for schema generation
└── settings/
    └── base.py                     # add health app and optional logger namespace

health/
├── __init__.py
├── apps.py
├── models.py                       # no persistence tables; included for app-layout compliance
├── selectors.py                    # intentionally minimal/unused read layer placeholder
├── services.py                     # application-process health evaluation
├── serializers.py                  # dedicated output serializer for health status
├── views.py                        # thin anonymous GET endpoint, no throttling
├── urls.py                         # api_v1_urlpatterns export for /api/v1/health/
└── tests/
    ├── test_services.py
    ├── test_api_health.py
    └── test_api_docs.py

docs/
└── api/
    ├── openapi-public.yaml
    └── openapi-internal.yaml
```

**Structure Decision**: Create a dedicated `health` app instead of placing the endpoint directly in
`afrourban/` or reusing `users`/`profiles`. The feature is operationally distinct, benefits from the
required app layout, and needs no database models or migrations.

## Phase 1 Design Artifacts

- [data-model.md](data-model.md): Defines conceptual health-evaluation entities, validation rules,
  and lifecycle transitions.
- [contracts/health-endpoint.md](contracts/health-endpoint.md): Defines the public endpoint
  contract, status semantics, documentation visibility, and logging expectations.
- [quickstart.md](quickstart.md): Ordered implementation and validation workflow, including test-
  first steps and schema verification.

## Constitution Check (Post-Design Re-check)

| Principle | Status | Notes |
|-----------|--------|-------|
| I. HackSoftware Styleguide | PASS | Design keeps view logic thin and isolates evaluation in `health/services.py` with a dedicated serializer |
| II. API-First Design | PASS | Contract fixes `/api/v1/health/`, public-doc visibility, and schema validation; exception for status-only `503` body remains explicitly documented |
| III. Test-First Development | PASS | Quickstart starts with failing service/API/schema tests before production changes |
| IV. Code Quality | PASS | Post-change validation includes Ruff, mypy, pytest, and spectacular validation |
| V. Structured Observability | PASS | Design includes structured health-check logs without leaking dependency or secret detail |
| VI. Simplicity & Reuse | PASS | Reuses existing DRF and schema infrastructure; no database or external dependency probes added |
| VII. Poetry-Managed Toolchain | PASS | All setup, validation, and schema-generation commands use `poetry run` |

**Post-Phase 1 gate: PASS** — ready for `/speckit.tasks`.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Status-only non-healthy `503` response body for `/api/v1/health/` instead of RFC 9457 Problem Details | The clarified feature contract requires the same single-field machine-readable body for both healthy and non-healthy results so monitors and frontend callers can parse one invariant shape | Returning Problem Details for `503` would violate the approved health contract and force client branching for a deliberately narrow operational signal |
