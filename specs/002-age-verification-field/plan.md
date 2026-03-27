# Implementation Plan: Age Verification Field

**Branch**: `002-age-verification-field` | **Date**: 27 March 2026 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-age-verification-field/spec.md`
**Depends on**: Feature 001 (Custom User & Profile Management)

## Summary

Extend the existing Profile model with age verification infrastructure: add `age_verification_status` and `age_verified_at` fields, implement age calculation from existing `date_of_birth`, and integrate minimum_age conditions into the Policy model. Age data is embedded in JWT private claims for stateless policy enforcement. Implementation follows HackSoftware Django Styleguide.

## Technical Context

**Language/Version**: Python ^3.11  
**Primary Dependencies**: Django 5.1.x, djangorestframework, djangorestframework-simplejwt (from feature 001)  
**Storage**: PostgreSQL (via psycopg2-binary)  
**Testing**: pytest, pytest-django, factory_boy  
**Target Platform**: Linux server (Docker/docker-compose)
**Project Type**: web-service (extension of feature 001)  
**Performance Goals**: Age calculation sub-10ms, policy checks sub-50ms  
**Constraints**: Date of birth stored securely, not exposed in public APIs; age computed dynamically  
**Scale/Scope**: Extends existing Profile model (~2 new fields), extends Policy conditions (minimum_age)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Compliance Notes |
|-----------|--------|------------------|
| I. HackSoftware Django Styleguide | ✅ PASS | Age calculation in services.py, not model methods. Dedicated serializers for age data output. |
| II. API-First Design | ✅ PASS | Profile API extended with age verification fields. RFC 9457 error format for validation errors. |
| III. Test-First Development | ✅ PASS | pytest with factory_boy. Unit tests for age calculation, integration tests for API. |
| IV. Code Quality Enforcement | ✅ PASS | Ruff linting, mypy strict mode, all functions typed. |
| V. Structured Observability | ✅ PASS | Log age verification status changes with user context. |
| VI. Simplicity & Reuse | ✅ PASS | Extends existing Profile/Policy models. Uses Python's datetime for age calculation (no new deps). |
| VII. Poetry-Managed Toolchain | ✅ PASS | No new dependencies required. All commands via `poetry run`. |

**Gate Result**: PASSED — Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/002-age-verification-field/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── age-verification.md  # Age verification API extensions
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
profiles/                 # Extended from feature 001
├── models.py            # Add age_verification_status, age_verified_at to Profile
├── services.py          # Add age calculation, verification status transitions
├── selectors.py         # Add age-related queries
├── serializers.py       # Add age output serializers (no date_of_birth exposure)
└── tests/
    ├── test_services.py # Age calculation tests
    └── test_views.py    # API integration tests

users/                    # Extended from feature 001
├── serializers.py       # Extend JWT claims with age data
└── tests/
    └── test_jwt_claims.py  # Verify age claims in token
```

**Structure Decision**: Extends existing `profiles` app from feature 001. No new Django apps required. Model migrations add fields to existing Profile table.

## Complexity Tracking

> No constitution violations. Feature is a straightforward extension of existing models.

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Age calculation | Dynamic property, not stored | Always reflects current date; no stale data risk |
| JWT age claims | Include age + verification status, not date_of_birth | Privacy compliance (FR-013) + stateless policy checks |
| Status enum | TextChoices with reserved values | Future-proof for document verification without migration |
