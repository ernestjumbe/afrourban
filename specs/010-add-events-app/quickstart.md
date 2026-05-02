# Quickstart: Events App

**Feature**: 010-add-events-app  
**Branch**: `010-add-events-app`

## Prerequisites

- Python 3.11+
- Poetry installed
- Database available and migrations up to date
- Feature branch checked out

## Setup

```bash
git checkout 010-add-events-app
poetry install
```

## Implementation Order (Test-First)

### 1. Write failing tests first

```bash
poetry run pytest events/tests/test_services.py -q
poetry run pytest events/tests/test_selectors.py -q
poetry run pytest events/tests/test_api_create.py -q
poetry run pytest events/tests/test_api_detail.py -q
poetry run pytest events/tests/test_api_cover.py -q
poetry run pytest events/tests/test_api_versioning.py -q
poetry run pytest events/tests/test_api_docs.py -q
```

Coverage targets for this feature:

- authenticated user can create a personal event with required fields
- organization owner can create an event for an owned organization
- non-owner cannot create or update an organization-owned event
- omitted category defaults to `other`
- `end_at` must be later than `start_at`
- physical locations require `country`, `state`, `city`, and `postcode`
- web locations require `web_url` and clear physical-address fields
- organizer context cannot be changed after creation
- updates to title, start time, end time, and location create immutable audit rows
- updates to non-audited fields do not create audit rows
- cover-image upload, replace, and delete flows work as documented
- `/api/v1/events/` routes and internal schema entries are present

### 2. Implement the new app and data model

- Create the `events` app with the standard project layout.
- Register the app and logger namespace in `afrourban/settings/base.py`.
- Add `Event` and `EventAuditEntry` models, admin registration, and initial migration.
- Add event test factories and helper payload builders.

```bash
poetry run python manage.py makemigrations events
poetry run python manage.py migrate
```

### 3. Implement selectors, services, serializers, and views

- Add selectors for event detail reads with organizer relations loaded.
- Add services for create/update, cover upload/delete, and audit-entry creation.
- Add dedicated input/output serializers with nested location validation.
- Add versioned API views and route registration in `afrourban/urls.py`.
- Emit structured event logs for successful mutations, denied writes, and validation failures.

### 4. Refresh API documentation and run validation gates

```bash
poetry run ruff check .
poetry run mypy .
poetry run pytest -q
poetry run python manage.py spectacular --settings=afrourban.settings.test --validate --file /tmp/openapi-010-validate.yaml
```

### 5. Final Validation Results

Validation was rerun on 2026-04-28 after completing the admin surface and
schema publication work:

```bash
poetry run ruff check .
poetry run mypy .
poetry run pytest
poetry run python manage.py spectacular --settings=afrourban.settings.test --validate --file /tmp/openapi-010-validate.yaml
```

Recorded outcomes:

- `poetry run ruff check .` -> passed (`All checks passed!`)
- `poetry run mypy .` -> passed (`Success: no issues found in 124 source files`)
- `poetry run pytest` -> passed (`198 passed in 2.36s`)
- `poetry run python manage.py spectacular --settings=afrourban.settings.test --validate --file /tmp/openapi-010-validate.yaml`
  -> passed with `0` schema errors and `3` operationId collision warnings
  outside the events surface

## Manual Verification Checklist

### Event Creation

1. `POST /api/v1/events/` with valid personal-event data succeeds.
2. `POST /api/v1/events/` with `organization_id` owned by the requester succeeds.
3. `POST /api/v1/events/` with `organization_id` not owned by the requester returns `403`.
4. `POST /api/v1/events/` without `category` saves the event with `category="other"`.
5. `POST /api/v1/events/` with `end_at <= start_at` fails with validation feedback.

### Location Validation and Updates

1. A physical-location event without `country`, `state`, `city`, or `postcode` is rejected.
2. A web-location event without `web_url` is rejected.
3. `PATCH /api/v1/events/{id}/` can switch an event from web to physical location.
4. `PATCH /api/v1/events/{id}/` can switch an event from physical to web location.
5. `PATCH /api/v1/events/{id}/` cannot change the organizer context.

### Audit Retention

1. Updating `title` creates one audit row with old/new values and actor metadata.
2. Updating `start_at` or `end_at` creates audit rows for the changed fields only.
3. Updating `location` creates an audit row that captures the full normalized old and new location
   states.
4. Updating `description`, `category`, or `tickets_url` alone does not create audit rows.

### Cover Image

1. `POST /api/v1/events/{id}/cover/` uploads a valid cover image.
2. Uploading a new cover image replaces the previous one.
3. `DELETE /api/v1/events/{id}/cover/` removes the stored image.
4. Unauthorized cover-image mutations return `403`.

### Documentation

1. Internal OpenAPI schema includes the events endpoints.
2. Public OpenAPI schema does not include the events endpoints.
3. `docs/api/endpoints.md` documents the authenticated-only events namespace and supported routes.

## Compatibility & Scope Notes

- This is an additive `/api/v1/` feature.
- No existing route is deprecated or replaced.
- Anonymous public event reads are not part of this iteration.
- Event collection/discovery APIs are intentionally deferred beyond this feature scope.
- Organizer transfer, event recurrence, cancellation workflows, attendee management, and end-user
  audit-history browsing are deferred beyond this feature scope.

## Expected Artifacts

- New `events` Django app with models, selectors, services, serializers, views, URLs, admin, and
  tests
- Initial migrations for event persistence and audit persistence
- Versioned events API endpoints under `/api/v1/events/`
- Updated OpenAPI docs and endpoint inventory documentation
- Passing quality gates (`ruff`, `mypy`, `pytest`, `spectacular --validate`)
