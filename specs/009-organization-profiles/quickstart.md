# Quickstart: Organization Profiles

**Feature**: 009-organization-profiles  
**Branch**: `009-organization-profiles`

## Prerequisites

- Python 3.11+
- Poetry installed
- Database available and migrations up to date
- Feature branch checked out

## Setup

```bash
git checkout 009-organization-profiles
poetry install
```

## Implementation Order (Test-First)

### 1. Write failing tests first

```bash
poetry run pytest organizations/tests/test_services.py -q
poetry run pytest organizations/tests/test_selectors.py -q
poetry run pytest organizations/tests/test_api_collection.py -q
poetry run pytest organizations/tests/test_api_detail.py -q
poetry run pytest organizations/tests/test_api_branding.py -q
poetry run pytest organizations/tests/test_api_versioning.py -q
poetry run pytest organizations/tests/test_api_docs.py -q
```

Coverage targets for this feature:

- owner can create an organization with required metadata
- duplicate names for the same owner are rejected while other owners may reuse the name
- physical organizations require an address
- online-only organizations may omit the address and clear it on update
- non-owners cannot patch or change branding
- collection filtering, pagination, and sorting behave as documented
- logo and cover image upload/replace/delete flows work as documented
- `/api/v1/organizations/` routes and schema entries are present

### 2. Implement the new app and data model

- Create the `organizations` app with the standard project layout.
- Register the app in `afrourban/settings/base.py`.
- Add `Organization` model, admin registration, and initial migration.
- Add organization test factories.

```bash
poetry run python manage.py makemigrations organizations
poetry run python manage.py migrate
```

### 3. Implement selectors, services, serializers, and views

- Add selectors for collection/detail reads with owner/type/presence filters.
- Add services for create/update and branding mutations.
- Add dedicated input/output serializers.
- Add versioned API views and route registration in `afrourban/urls.py`.
- Emit structured organization events for successful and denied mutations.

### 4. Refresh API documentation and run validation gates

```bash
poetry run ruff check .
poetry run mypy .
poetry run pytest -q
poetry run python manage.py spectacular --settings=afrourban.settings.test --validate --file /tmp/openapi-009-validate.yaml
```

## Manual Verification Checklist

### Organization Creation and Update

1. `POST /api/v1/organizations/` with valid physical-organization data succeeds.
2. `POST /api/v1/organizations/` without `physical_address` while `is_online_only=false` fails with validation feedback.
3. `POST /api/v1/organizations/` with `is_online_only=true` and no address succeeds.
4. `PATCH /api/v1/organizations/{id}/` by the owner updates the organization successfully.
5. `PATCH /api/v1/organizations/{id}/` by a non-owner returns `403`.

### Duplicate Names and Filtering

1. Creating the same organization name twice for one owner is rejected.
2. Creating the same organization name under different owners is allowed.
3. `GET /api/v1/organizations/?owner_scope=mine` returns only the requester’s organizations.
4. `GET /api/v1/organizations/?organization_type=restaurant&is_online_only=false` filters correctly.
5. `GET /api/v1/organizations/?ordering=name&page=1&page_size=20` returns the documented pagination envelope.

### Branding

1. `POST /api/v1/organizations/{id}/logo/` uploads a valid logo.
2. `POST /api/v1/organizations/{id}/cover/` uploads a valid cover image.
3. Uploading a new asset replaces the previous one in the same slot.
4. `DELETE` on logo/cover endpoints removes the stored asset.
5. Non-owner branding mutations return `403`.

### Documentation

1. Public and internal OpenAPI schemas include the organizations endpoints.
2. Docs reflect `/api/v1/organizations/` routing and the pagination/filtering contract.
3. Docs describe owner-only writes and separate branding endpoints.

## Compatibility & Scope Notes

- This is an additive `/api/v1/` feature.
- No existing route is deprecated or replaced.
- Anonymous public organization reads are not part of this iteration.
- Organization deletion and ownership transfer are deferred beyond this feature scope.

## Expected Artifacts

- New `organizations` Django app with model, selectors, services, serializers, views, URLs, admin, and tests
- Initial migration for organization persistence
- Versioned organizations API endpoints under `/api/v1/organizations/`
- Updated OpenAPI docs and endpoint documentation
- Passing quality gates (`ruff`, `mypy`, `pytest`, `spectacular --validate`)

## Latest Validation Results

Validation run completed on 2026-04-27 against `afrourban.settings.test`.

- `poetry run ruff check .` — passed
- `poetry run mypy .` — passed (`Success: no issues found in 103 source files`)
- `poetry run pytest` — passed (`158 passed`)
- `poetry run python manage.py spectacular --settings=afrourban.settings.test --validate --file /tmp/openapi-009-validate.yaml` — passed with 3 operationId collision warnings and 0 schema errors
- `docs/api/openapi-public.yaml` and `docs/api/openapi-internal.yaml` were regenerated from the scoped schema views

Notes from the validation pass:

- Test settings now override cache storage to `LocMemCache` so repo-wide test runs do not require a live Redis service.
- The spectacular validation warnings are existing operationId naming collisions for admin and organizations `GET` routes; schema validation still completed successfully with zero errors.
