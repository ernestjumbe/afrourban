# Implementation Plan: Username Registration and Email Privacy

**Branch**: `006-add-username-privacy` | **Date**: 2026-03-28 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-add-username-privacy/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Introduce a first-class `username` attribute on the custom user model while keeping authentication on
email/password, require username at registration, backfill missing usernames for existing users from
email, enforce clarified username format and case-insensitive uniqueness, and add authenticated
username change with configurable cooldown (default 7 days). In parallel, enforce email-privacy
projection rules so non-privileged requesters never receive non-owned user emails, while authorized
admin/staff operations retain access.

## Technical Context

**Language/Version**: Python 3.11 (project constraint `^3.11`)  
**Primary Dependencies**: Django 5.1.2, Django REST Framework, SimpleJWT, drf-spectacular, structlog  
**Storage**: Django ORM on PostgreSQL (production) / SQLite (dev+test), with new user-field migration  
**Testing**: pytest + pytest-django + factory_boy (unit/service/integration/contract tests)  
**Target Platform**: Linux containerized web service (Docker Compose), local macOS development  
**Project Type**: Django REST API service  
**Performance Goals**: No observable regression on auth/profile endpoints; username-cooldown checks rely on indexed user lookups and constant-time timestamp comparison  
**Constraints**: Keep email as login identifier; enforce case-insensitive username uniqueness; default cooldown=7 days configurable in days; apply no cooldown after initial username creation; enforce ownership/role-based email visibility in all API response objects; preserve `/api/v1/` routing and `api_urlpatterns` registration  
**Scale/Scope**: CustomUser schema evolution, registration/auth/admin/profile response adjustments, one new authenticated username-change endpoint, docs/schema updates, and full automated coverage

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. HackSoftware Styleguide | PASS | Mutations remain in services, reads in selectors, serializers/views stay orchestration-only |
| II. API-First Design | PASS | API changes remain under `/api/v1/`, OpenAPI updated via drf-spectacular, routes continue through `api_urlpatterns` |
| III. Test-First Development | PASS | Plan includes failing tests first for registration, migration/backfill, cooldown, privacy projection |
| IV. Code Quality | PASS | Plan includes `ruff`, `mypy`, `pytest`, and `spectacular --validate` |
| V. Structured Observability | PASS | Plan includes structured log events for username change attempts and redaction decisions |
| VI. Simplicity & Reuse | PASS | Uses existing users app/settings/services/serializers patterns; avoids new app or extra persistence tables |
| VII. Poetry-Managed Toolchain | PASS | All implementation and validation commands specified with `poetry run` |

**Pre-Phase 0 gate: PASS** — no constitution violations.

## Phase 0 Research Summary

Research decisions are captured in [research.md](research.md), covering:

1. CustomUser schema strategy for username + cooldown timestamp
2. Backfill policy for existing users with missing/blank usernames
3. Username validation/uniqueness enforcement boundaries
4. Username change endpoint and cooldown configuration model
5. Ownership/role-based email redaction contract across API responses
6. Test and observability strategy for compliance and regression control

## Project Structure

### Documentation (this feature)

```text
specs/006-add-username-privacy/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── username-and-email-privacy.md
└── tasks.md
```

### Source Code (repository root)

```text
afrourban/
├── urls.py                         # verify api_urlpatterns coverage for any new route
└── settings/
    └── base.py                     # cooldown setting override surface (if centralized)

users/
├── conf.py                         # add USERS_USERNAME_CHANGE_COOLDOWN_DAYS accessor
├── models.py                       # add username fields/constraints metadata
├── migrations/                     # schema + data migration for username backfill
├── services.py                     # registration/create + username-change business rules
├── selectors.py                    # ownership/visibility helper selectors if needed
├── serializers.py                  # registration + response redaction + username-change serializers
├── views.py                        # add username-change endpoint orchestration
├── urls.py                         # mount new endpoint under /api/v1/auth/
└── tests/
    ├── test_registration.py
    ├── test_username_change.py
    ├── test_api_email_visibility.py
    ├── test_migrations_username_backfill.py
    └── test_api_docs.py

profiles/
├── serializers.py                  # ensure non-owned profile output never leaks email
└── tests/
    └── test_api_email_visibility.py

docs/
└── api/
    ├── endpoints.md                # endpoint behavior updates
    └── openapi-*.yaml              # regenerated schema artifacts
```

**Structure Decision**: Implement entirely within existing `users`, `profiles`, and project routing/settings
modules to preserve established architecture and minimize migration risk.

## Phase 1 Design Artifacts

- [data-model.md](data-model.md): Defines user/username/cooldown and response-projection entities,
  constraints, and transitions.
- [contracts/username-and-email-privacy.md](contracts/username-and-email-privacy.md): Defines
  registration, username-change, and email-visibility API contracts.
- [quickstart.md](quickstart.md): Ordered implementation and validation workflow, including migration
  and quality gates.

## Constitution Check (Post-Design Re-check)

| Principle | Status | Notes |
|-----------|--------|-------|
| I. HackSoftware Styleguide | PASS | Design keeps mutation logic in services and projection logic in serializers/selectors |
| II. API-First Design | PASS | Contract defines `/api/v1/` changes, schema/doc updates, and `api_urlpatterns` compliance |
| III. Test-First Development | PASS | Quickstart starts with failing tests for each story before implementation |
| IV. Code Quality | PASS | Validation workflow includes Ruff, mypy, pytest, and spectacular validation |
| V. Structured Observability | PASS | Explicit structured events included for cooldown and redaction decisions |
| VI. Simplicity & Reuse | PASS | Reuses existing Django app structure; no unnecessary new abstractions |
| VII. Poetry-Managed Toolchain | PASS | All commands remain Poetry-managed |

**Post-Phase 1 gate: PASS** — ready for `/speckit.tasks`.

## Complexity Tracking

> No constitution violations requiring justification.
