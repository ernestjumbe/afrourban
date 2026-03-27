# Implementation Plan: Custom User & Profile Management

**Branch**: `001-user-profile-apps` | **Date**: 27 March 2026 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-user-profile-apps/spec.md`

## Summary

Implement custom Django user and profile management with JWT-based authentication using Django Simple JWT. The system provides user registration, authentication (with private claims for policies), profile management, permission-based access control, and role/policy management. Implementation follows HackSoftware Django Styleguide with services/selectors pattern.

## Technical Context

**Language/Version**: Python ^3.11  
**Primary Dependencies**: Django 5.1.x, djangorestframework, djangorestframework-simplejwt, Pillow  
**Storage**: PostgreSQL (via psycopg2-binary)  
**Testing**: pytest, pytest-django, factory_boy  
**Target Platform**: Linux server (Docker/docker-compose)
**Project Type**: web-service  
**Performance Goals**: 500+ concurrent authenticated users, sub-200ms permission check overhead  
**Constraints**: JWT access token 30min expiry, refresh token 1 day, temporary lockout 15-30 min after 5 failed attempts  
**Scale/Scope**: Multi-user application with RBAC, 5 core entities (User, Profile, Permission, Role, Policy)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Compliance Notes |
|-----------|--------|------------------|
| I. HackSoftware Django Styleguide | ✅ PASS | Services/selectors pattern for all business logic. Thin models. Dedicated input/output serializers. |
| II. API-First Design | ✅ PASS | All features exposed as REST API endpoints first. RFC 9457 Problem Details for errors. |
| III. Test-First Development | ✅ PASS | pytest with factory_boy. Unit tests for services/selectors, integration tests for API contracts. |
| IV. Code Quality Enforcement | ✅ PASS | Ruff linting, mypy strict mode, all functions typed. |
| V. Structured Observability | ✅ PASS | JSON logging with structlog. Request-scoped context (user_id, request_id). Audit logging for auth events. |
| VI. Simplicity & Reuse | ✅ PASS | Using djangorestframework-simplejwt (established package). No speculative abstractions. |
| VII. Poetry-Managed Toolchain | ✅ PASS | All deps in pyproject.toml. All commands via `poetry run`. |

**Gate Result**: PASSED — Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/001-user-profile-apps/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── auth.md          # Authentication endpoints
│   ├── profiles.md      # Profile management endpoints
│   └── admin.md         # Admin/permission endpoints
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
users/                    # Custom user app
├── __init__.py
├── admin.py
├── apps.py
├── models.py            # CustomUser model
├── services.py          # Registration, auth, password services
├── selectors.py         # User queries
├── serializers.py       # Input/output serializers
├── views.py             # API views
├── urls.py
├── permissions.py       # DRF permission classes
└── tests/
    ├── __init__.py
    ├── factories.py
    ├── test_services.py
    ├── test_selectors.py
    └── test_views.py

profiles/                 # Profile app
├── __init__.py
├── admin.py
├── apps.py
├── models.py            # Profile, Permission, Role, Policy models
├── services.py          # Profile CRUD, permission assignment
├── selectors.py         # Profile/permission queries
├── serializers.py
├── views.py
├── urls.py
└── tests/
    ├── __init__.py
    ├── factories.py
    ├── test_services.py
    ├── test_selectors.py
    └── test_views.py

afrourban/
├── settings/            # Existing settings (add JWT config)
└── urls.py              # Add users/, profiles/ routes
```

**Structure Decision**: Two separate Django apps (`users`, `profiles`) following HackSoftware Styleguide directory layout. Users app handles authentication/authorization; Profiles app handles extended user data, roles, permissions, and policies.

## Complexity Tracking

> No constitution violations requiring justification. Design follows all 7 principles.

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Two Django apps | users + profiles | Separation of concerns: auth vs extended data. Both apps remain small and focused. |
| JWT with private claims | Custom TokenObtainPairSerializer | Established pattern in djangorestframework-simplejwt. Embeds policies in token to reduce DB lookups. |
| Policy in JWT | Embed active policies as claim | Trade-off: larger token vs fewer permission checks. Acceptable for auth-heavy operations. |
