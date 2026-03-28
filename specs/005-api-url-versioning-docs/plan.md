# Implementation Plan: API URL Versioning and Documentation

**Branch**: `005-api-url-versioning-docs` | **Date**: 2026-03-28 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-api-url-versioning-docs/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Reorganize all active API endpoints under a canonical `/api/v1/` namespace, remove unversioned
legacy routes in the same release, and establish constitution-compliant API documentation generation
with `drf-spectacular` (OpenAPI 3.0+). The implementation introduces centralized
`api_urlpatterns` registration in main `urls.py`, split documentation visibility
(public vs authenticated/internal), complete endpoint coverage including restricted/admin routes, and
explicit deprecation policy enforcement with a minimum 90-day notice window.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Django 5.1.2, Django REST Framework, SimpleJWT, drf-spectacular, structlog  
**Storage**: PostgreSQL (production), SQLite (local/test); no new persistent feature tables required  
**Testing**: pytest + pytest-django + factory_boy; API integration and contract coverage required  
**Target Platform**: Linux Docker deployment, local macOS development  
**Project Type**: Django REST API service  
**Performance Goals**: Versioned routing adds no meaningful overhead; schema generation validates in CI and release checks  
**Constraints**: No unversioned legacy routes after release; future deprecations require >=90 days notice; internal docs must include all endpoints  
**Scale/Scope**: Migrate and document all active endpoints from `users` and `profiles` apps under `/api/v1/`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. HackSoftware Styleguide | PASS | URL and documentation wiring only; services/selectors architecture remains intact |
| II. API-First Design | PASS | Versioned `/api/v1/` routes, `api_urlpatterns`, OpenAPI 3.0+ via drf-spectacular |
| III. Test-First Development | PASS | Plan includes route, schema, and deprecation-policy validation tests |
| IV. Code Quality | PASS | ruff, mypy, pytest, and `manage.py spectacular --validate` included |
| V. Structured Observability | PASS | Routing/docs/deprecation events planned for structured logs |
| VI. Simplicity & Reuse | PASS | Reuses drf-spectacular and existing URL modules; avoids bespoke doc tooling |
| VII. Poetry-Managed Toolchain | PASS | Dependency and validation commands run with `poetry run` |

**Pre-Phase 0 gate: PASS** — no constitution violations.

## Phase 0 Research Summary

Research decisions are captured in [research.md](research.md), covering:

1. Centralized `api_urlpatterns` architecture in main `urls.py`
2. Immediate legacy unversioned route removal strategy
3. drf-spectacular adoption and OpenAPI publication model
4. Two documentation visibility views (public vs authenticated/internal)
5. Deprecation policy data requirements and 90-day notice enforcement
6. Route inventory and schema validation test strategy

## Project Structure

### Documentation (this feature)

```text
specs/005-api-url-versioning-docs/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api-versioning-and-documentation.md
└── tasks.md
```

### Source Code (repository root)

```text
afrourban/
├── urls.py                    # define api_urlpatterns and include under /api/
└── settings/
    └── base.py               # drf-spectacular + schema settings

users/
├── urls.py                   # expose version-ready auth/admin route groups
├── views.py                  # optional schema annotations where needed
└── tests/
    ├── test_api_versioning.py
    └── test_api_docs.py

profiles/
├── urls.py                   # expose version-ready profile route groups
└── tests/
    └── test_api_versioning.py

docs/
└── api/
    └── deprecations.md       # deprecation date, removal date, migration path
```

**Structure Decision**: Keep routing and documentation changes within existing `afrourban`,
`users`, and `profiles` modules. No new Django app is required. This minimizes churn while
fulfilling the constitution's versioning and documentation mandates.

## Phase 1 Design Artifacts

- [data-model.md](data-model.md): Defines conceptual entities for API versions, route registry,
  documentation views, and deprecation notices.
- [contracts/api-versioning-and-documentation.md](contracts/api-versioning-and-documentation.md):
  Defines versioned path contract, endpoint visibility matrix, and deprecation contract rules.
- [quickstart.md](quickstart.md): Implementation and validation workflow for routing migration,
  schema generation, and compatibility checks.

## Constitution Check (Post-Design Re-check)

| Principle | Status | Notes |
|-----------|--------|-------|
| I. HackSoftware Styleguide | PASS | No new business logic added to views; existing layering preserved |
| II. API-First Design | PASS | Contract artifact captures all endpoints under `/api/v1/` and documentation visibility rules |
| III. Test-First Development | PASS | Quickstart and contracts define route/docs/deprecation tests before implementation completion |
| IV. Code Quality | PASS | Post-change validation includes ruff, mypy, pytest, spectacular schema validation |
| V. Structured Observability | PASS | Deprecation and route registration events specified for structured logging |
| VI. Simplicity & Reuse | PASS | Uses drf-spectacular and native Django URL includes; avoids custom schema engine |
| VII. Poetry-Managed Toolchain | PASS | All setup/validation commands remain Poetry-managed |

**Post-Phase 1 gate: PASS** — ready for `/speckit.tasks`.

## Complexity Tracking

> No constitution violations requiring justification.
