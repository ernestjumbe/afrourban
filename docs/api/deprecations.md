# API Deprecation Policy and Migration Guidance

This document defines how Afrourban deprecates API versions and endpoints.
Machine-readable entries are maintained in `docs/api/deprecations.yaml`.

## Policy Requirements

Every deprecated version or endpoint MUST provide:

- `deprecation_date` (ISO `YYYY-MM-DD`)
- `removal_date` (ISO `YYYY-MM-DD`)
- `migration_path` (explicit replacement path or migration steps)

Notice window rule:

- `removal_date` MUST be at least 90 days after `deprecation_date`.

## Registry Structure

The deprecation registry contains:

- `policy`: global notice and required-field rules
- `versions`: version-level lifecycle entries (for example `v1`, `v2`)
- `endpoints`: endpoint-level deprecation entries
- `examples`: non-enforced templates for future additions

## Current State

- Default active version: `v1`
- No version or endpoint currently marked as deprecated

## Deprecation Workflow

1. Add or update entries in `docs/api/deprecations.yaml`.
2. Ensure all deprecated entries include complete metadata and satisfy the 90-day notice policy.
3. Validate the registry:
   - `poetry run python manage.py validate_api_deprecations`
4. Regenerate and validate OpenAPI output:
   - `poetry run python manage.py spectacular --file /tmp/openapi.yaml --validate`
5. Confirm internal docs publish deprecation metadata under `x-deprecations`.

## Migration Guidance Standards

`migration_path` must be actionable. Acceptable examples:

- Replacement endpoint path: `/api/v2/auth/token/`
- Link to a migration runbook with ordered steps
- Short, explicit instructions when no direct endpoint replacement exists
