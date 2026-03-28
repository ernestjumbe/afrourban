# Research: API URL Versioning and Documentation

**Feature**: 005-api-url-versioning-docs  
**Date**: 2026-03-28

## 1. Main API Routing Topology

### Decision

Define a single `api_urlpatterns` list in `afrourban/urls.py` and include it under `/api/`, with
versioned group entrypoints (`/api/v1/...`) only.

### Rationale

This directly satisfies the constitution rule that all API URLs are registered in
`api_urlpatterns` in main `urls.py`, then included under `/api/`. It also centralizes route
inventory control for documentation and migration checks.

### Alternatives considered

- Keep app-level includes directly at `/api/` without `api_urlpatterns`: rejected because it
  violates the constitution amendment.
- Move all routes into a monolithic URL file: rejected due to maintainability and app ownership
  concerns.

## 2. Legacy Unversioned Route Migration

### Decision

Remove legacy unversioned routes in the same release as `/api/v1/` rollout.

### Rationale

Clarification session explicitly chose immediate removal. This prevents dual-path drift and enforces
a single canonical API contract.

### Alternatives considered

- Temporary dual-serving with sunset window: rejected by clarification answer.
- Redirect unversioned to versioned endpoints: rejected because behavior can be ambiguous for
  non-idempotent requests and delays cleanup.

## 3. API Documentation Standard

### Decision

Use `drf-spectacular` as the single schema generator and publish OpenAPI 3.0+ output.

### Rationale

Constitution Principle II requires generated/maintained documentation with drf-spectacular. The
library integrates natively with DRF and supports schema validation in CI.

### Alternatives considered

- drf-yasg: rejected due to constitution mandate and redundant tooling.
- Manually maintained endpoint docs only: rejected because it is error-prone and non-authoritative.

## 4. Documentation Visibility Model

### Decision

Publish two documentation views:

- Public docs: public endpoints only
- Authenticated/internal docs: complete endpoint set including restricted/admin routes

### Rationale

Clarifications require full endpoint documentation while keeping public visibility limited to public
operations. Dual-view publication satisfies both coverage and visibility controls.

### Alternatives considered

- Single public doc containing all endpoints: rejected due to unnecessary exposure of restricted
  operations.
- Internal-only docs for everything: rejected because public endpoints should remain discoverable.

## 5. Deprecation Policy Enforcement

### Decision

Deprecation records must include `deprecation_date`, `removal_date`, and `migration_path`, with a
minimum 90-day notice between deprecation and removal for future API removals.

### Rationale

This matches clarified requirements and makes deprecation policy auditable through documentation and
release checks.

### Alternatives considered

- No minimum removal window: rejected as incompatible with clarified policy.
- 30-day notice window: rejected by clarification answer.

## 6. Backward Compatibility Policy for `/api/v1/`

### Decision

Preserve behavior and documented contract semantics for `/api/v1/`; allow additive,
backward-compatible changes (for example optional fields).

### Rationale

This was explicitly chosen in clarifications and balances stability with pragmatic iteration.

### Alternatives considered

- Strict freeze (no additive fields): rejected as unnecessarily restrictive.
- Permit breaking changes in v1 with docs update: rejected due to client breakage risk.

## 7. Validation and Test Approach

### Decision

Use a three-layer validation approach:

1. URL resolution tests for versioned endpoint inventory
2. Schema generation/validation checks via `manage.py spectacular --validate`
3. Contract checks that public docs exclude restricted/admin endpoints and internal docs include all

### Rationale

This directly validates the success criteria for route reachability, documentation completeness,
and visibility partitioning.

### Alternatives considered

- Manual QA only: rejected due to high regression risk.
- Schema validation without route inventory tests: rejected because docs could still drift from
  runtime URLs.
