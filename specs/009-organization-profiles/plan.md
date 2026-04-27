# Implementation Plan: Organization Profiles

**Branch**: `009-organization-profiles` | **Date**: 2026-04-25 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/009-organization-profiles/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add a dedicated `organizations` Django app that models business and community entities separately
from individual `Profile` records and exposes versioned REST endpoints for authenticated
organization listing, creation, detail retrieval, owner-only updates, and separate logo/cover media
management. The design keeps write logic in services, read logic in selectors, applies
per-owner case-insensitive name uniqueness, and enforces the physical-address requirement only when
an organization is not marked online-only.

## Technical Context

**Language/Version**: Python 3.11 (project constraint `^3.11`)  
**Primary Dependencies**: Django 5.1.2, Django REST Framework 3.17.1, drf-spectacular 0.29.0, SimpleJWT 5.5.1, Pillow 12.1.1, structlog 25.2.0  
**Storage**: Django ORM on PostgreSQL (production) / SQLite (dev+test), with one new `organizations_organization` table and media file references for logo/cover assets  
**Testing**: pytest + pytest-django + factory_boy for service, selector, API, routing, and schema tests  
**Target Platform**: Linux containerized web service (Docker Compose), local macOS development  
**Project Type**: Django REST API service  
**Performance Goals**: Paginated organization collections should return default page results without noticeable delay; organization create/update flows remain single-record transactions; image upload validation should stay consistent with current profile-avatar expectations  
**Constraints**: Preserve strict separation between person profiles and organization entities; keep routes under `/api/v1/` and main `api_urlpatterns`; collection endpoints must support filtering, pagination, and sorting; reads are authenticated in v1; non-owner mutations must be blocked; physical address is required only when `is_online_only=false`; branding uploads must reuse existing image-validation conventions  
**Scale/Scope**: One new Django app, one primary model, list/create/detail/update APIs, separate logo/cover upload endpoints, schema/docs updates, migrations, admin registration, structured logging, and full automated coverage

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. HackSoftware Styleguide | PASS | New app will keep mutations in `services.py`, queries in `selectors.py`, thin models, dedicated serializers, and versioned API views |
| II. API-First Design | PASS | Plan defines `/api/v1/organizations/` resource contracts, filtering/pagination/sorting, OpenAPI updates, and main `api_urlpatterns` registration |
| II.a Deprecation Policy | PASS | Feature is additive under `/api/v1/`; no deprecated route/version is introduced |
| III. Test-First Development | PASS | Plan starts with failing tests for service rules, ownership enforcement, collection behavior, branding uploads, routing, and schema/docs |
| IV. Code Quality | PASS | Validation workflow includes `ruff`, `mypy`, `pytest`, and `manage.py spectacular --validate` |
| V. Structured Observability | PASS | Plan adds structured events for organization creation, update, branding mutation, and denied writes with actor/organization context |
| VI. Simplicity & Reuse | PASS | Reuses existing app patterns for services/selectors/APIView serializers, image handling, manual pagination envelope, and versioned routing |
| VII. Poetry-Managed Toolchain | PASS | All implementation, migration, test, and validation commands remain `poetry run ...` |

**Pre-Phase 0 gate: PASS** — no constitution violations.

## Phase 0 Research Summary

Research decisions are captured in [research.md](research.md), covering:

1. Why the new app should be named `organizations` and live as a first-class Django app
2. How organization names should be validated and de-duplicated without requiring global uniqueness
3. The authenticated `/api/v1/organizations/` endpoint surface, including list filtering, pagination, and sorting
4. Presence-mode rules for `is_online_only` and `physical_address`
5. Branding upload strategy for `logo` and `cover_image`
6. Observability, schema, and testing strategy for the new app

## Project Structure

### Documentation (this feature)

```text
specs/009-organization-profiles/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── organizations-api.md
└── tasks.md
```

### Source Code (repository root)

```text
afrourban/
├── urls.py                         # register organizations api_v1_urlpatterns
└── settings/
    └── base.py                     # install the organizations app and keep shared DRF/logging config

organizations/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── selectors.py
├── services.py
├── serializers.py
├── views.py
├── urls.py
├── permissions.py                  # owner-only write permission helper
├── migrations/
└── tests/
    ├── __init__.py
    ├── factories.py
    ├── test_services.py
    ├── test_selectors.py
    ├── test_api_collection.py
    ├── test_api_detail.py
    ├── test_api_branding.py
    ├── test_api_versioning.py
    └── test_api_docs.py

docs/
└── api/
    ├── endpoints.md                # document organizations endpoints and behaviors
    ├── openapi-public.yaml
    └── openapi-internal.yaml
```

**Structure Decision**: Implement the feature as a new top-level `organizations` Django app and
integrate it into existing project routing/settings so organization behavior stays isolated from the
`profiles` app while following the repository’s established app architecture.

## Phase 1 Design Artifacts

- [data-model.md](data-model.md): Defines the `Organization` entity, collection-query contract, and
  branding mutation rules.
- [contracts/organizations-api.md](contracts/organizations-api.md): Defines the versioned API
  surface for collection, detail, and branding endpoints.
- [quickstart.md](quickstart.md): Provides the ordered implementation and validation workflow,
  including migration and quality-gate steps.

## Constitution Check (Post-Design Re-check)

| Principle | Status | Notes |
|-----------|--------|-------|
| I. HackSoftware Styleguide | PASS | Design keeps business rules in services/selectors and uses dedicated input/output serializers |
| II. API-First Design | PASS | Contract defines `/api/v1/organizations/` resources, filter/sort/pagination behavior, schema updates, and main URL registration |
| II.a Deprecation Policy | PASS | No deprecated versions or endpoints introduced; additive release only |
| III. Test-First Development | PASS | Quickstart begins with failing tests for all new business and contract flows |
| IV. Code Quality | PASS | Validation sequence includes Ruff, mypy, pytest, and spectacular validation |
| V. Structured Observability | PASS | Explicit organization audit events are defined for create/update/branding/denial paths |
| VI. Simplicity & Reuse | PASS | Design reuses current image-upload, pagination-envelope, and APIView patterns instead of introducing new frameworks or abstractions |
| VII. Poetry-Managed Toolchain | PASS | All commands remain Poetry-managed |

**Post-Phase 1 gate: PASS** — ready for `/speckit.tasks`.

## Complexity Tracking

> No constitution violations requiring justification.
