# Implementation Plan: Events App

**Branch**: `010-add-events-app` | **Date**: 2026-04-27 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/010-add-events-app/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add a dedicated `events` Django app that supports authenticated creation and maintenance of
personal events and organization-owned events under `/api/v1/events/`. The design keeps organizer
ownership exclusive to either a user or an owned organization, models location as either a
structured physical address or a web address, manages optional cover images through dedicated media
endpoints, and persists immutable field-level audit entries for changes to title, start time, end
time, and location.

## Technical Context

**Language/Version**: Python 3.11 (project constraint `^3.11`)  
**Primary Dependencies**: Django 5.1.2, Django REST Framework 3.17.1, drf-spectacular 0.29.0, SimpleJWT 5.5.1, Pillow 12.1.1, structlog 25.2.0  
**Storage**: Django ORM on PostgreSQL (production) / SQLite (dev+test), with new `events_event` and `events_eventauditentry` tables plus media file references for optional cover images  
**Testing**: pytest + pytest-django + factory_boy for service, selector, API, routing, and schema tests  
**Target Platform**: Linux containerized web service (Docker Compose), local macOS development  
**Project Type**: Django REST API service  
**Performance Goals**: Event create/update flows remain single-event transactions; each successful audited update writes at most four audit rows; event detail reads should stay within the project’s normal single-resource query budget; cover upload validation should match existing organization/profile image expectations  
**Constraints**: Preserve versioned `/api/v1/` routing and `api_urlpatterns`; keep business logic in services/selectors; enforce end time later than start time; allow exactly one organizer context and exactly one location mode per event; retain immutable audit history for title/start/end/location for the lifetime of the event; keep authenticated-only visibility in v1 unless a later feature changes access scope; reuse existing Problem Details and image-validation patterns  
**Scale/Scope**: One new Django app, two primary persistence models, create/detail/update APIs, dedicated cover upload/delete endpoints, schema/docs updates, admin registration, structured logging, migrations, and full automated coverage

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. HackSoftware Styleguide | PASS | New `events` app will keep mutations in `services.py`, reads in `selectors.py`, models thin, and API views/serializers dedicated to input and output concerns |
| II. API-First Design | PASS | Plan defines versioned `/api/v1/events/` contracts, OpenAPI updates, internal-schema visibility, and main `api_urlpatterns` registration under `/api/` |
| II.a Deprecation Policy | PASS | Feature is additive under `/api/v1/`; no deprecated route or version is introduced |
| III. Test-First Development | PASS | Plan starts with failing tests for ownership rules, location validation, audit persistence, cover-image mutations, routing, and schema/docs |
| IV. Code Quality | PASS | Validation workflow includes `ruff`, `mypy`, `pytest`, and `manage.py spectacular --validate` |
| V. Structured Observability | PASS | Plan adds structured events for event create/update success, validation failures, cover mutations, and denied writes with actor and organizer context |
| VI. Simplicity & Reuse | PASS | Design reuses existing organization ownership helpers, Problem Details responses, image validation constraints, APIView patterns, and versioned routing rather than adding a history or media-management package |
| VII. Poetry-Managed Toolchain | PASS | All implementation, migration, test, and schema commands remain `poetry run ...` |

**Pre-Phase 0 gate: PASS** — no constitution violations.

## Phase 0 Research Summary

Research decisions are captured in [research.md](research.md), covering:

1. Why the feature should be implemented as a first-class `events` Django app
2. How a single event model should represent either personal or organization ownership without
   supporting organizer transfers
3. How event categories, location input, and optional cover media should be modeled in the v1 API
4. How immutable audit entries should be stored without introducing a third-party history package
5. Why v1 should expose create/detail/update and dedicated cover endpoints, but not a broader
   event-discovery collection
6. Observability, schema, and automated test strategy for the new app

## Project Structure

### Documentation (this feature)

```text
specs/010-add-events-app/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── events-api.md
└── tasks.md
```

### Source Code (repository root)

```text
afrourban/
├── urls.py                         # register events api_v1_urlpatterns under /api/v1/events/
└── settings/
    └── base.py                     # install the events app and logger namespace

events/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── selectors.py
├── services.py
├── serializers.py
├── views.py
├── urls.py
├── permissions.py                  # event write-access helpers for personal vs organization events
├── migrations/
└── tests/
    ├── __init__.py
    ├── factories.py
    ├── test_services.py
    ├── test_selectors.py
    ├── test_api_create.py
    ├── test_api_detail.py
    ├── test_api_cover.py
    ├── test_api_versioning.py
    └── test_api_docs.py

docs/
└── api/
    ├── endpoints.md                # document events endpoints and scope
    ├── openapi-public.yaml
    └── openapi-internal.yaml
```

**Structure Decision**: Implement the feature as a new top-level `events` Django app so event
ownership, validation, audit persistence, and cover-image behavior remain isolated from
`profiles` and `organizations` while following the repository’s established app architecture.

## Phase 1 Design Artifacts

- [data-model.md](data-model.md): Defines the `Event` and `EventAuditEntry` entities, location
  rules, and audit invariants.
- [contracts/events-api.md](contracts/events-api.md): Defines the versioned API surface for event
  create/detail/update and cover-image endpoints.
- [quickstart.md](quickstart.md): Provides the ordered implementation and validation workflow,
  including migration, schema, and quality-gate steps.

## Constitution Check (Post-Design Re-check)

| Principle | Status | Notes |
|-----------|--------|-------|
| I. HackSoftware Styleguide | PASS | Design keeps write logic in services, read logic in selectors, and uses dedicated serializers for nested location input/output |
| II. API-First Design | PASS | Contract defines `/api/v1/events/` resources, internal-schema visibility, OpenAPI updates, and main URL registration |
| II.a Deprecation Policy | PASS | No deprecated versions or endpoints introduced; release is additive only |
| III. Test-First Development | PASS | Quickstart begins with failing tests for ownership, schedule validation, location validation, audit creation, and media mutations |
| IV. Code Quality | PASS | Validation sequence includes Ruff, mypy, pytest, and spectacular validation |
| V. Structured Observability | PASS | Explicit structured event logs are defined for create/update/cover/denial paths with actor and organizer identifiers |
| VI. Simplicity & Reuse | PASS | Design reuses current authenticated API and image-upload patterns, keeps organizer context immutable, and avoids speculative listing/discovery features |
| VII. Poetry-Managed Toolchain | PASS | All commands remain Poetry-managed |

**Post-Phase 1 gate: PASS** — ready for `/speckit.tasks`.

## Complexity Tracking

> No constitution violations requiring justification.
