# Quickstart: Application Health Endpoint

**Feature**: 007-health-endpoint  
**Branch**: `007-health-endpoint`

## Prerequisites

- Python 3.11+
- Poetry installed
- Existing project dependencies installed with `poetry install`
- Local environment configured for the Django project

## Setup

```bash
git checkout 007-health-endpoint
poetry install
poetry run python manage.py migrate
```

No new migration is expected for this feature; `migrate` is included only to ensure the local
environment is current.

## Implementation Order

1. Create the `health` app skeleton and add it to `INSTALLED_APPS`.
2. Write failing tests first:
   - `health/tests/test_services.py`
   - `health/tests/test_api_health.py`
   - `health/tests/test_api_docs.py`
3. Implement the health evaluation service in `health/services.py`.
4. Add the dedicated output serializer and thin API view in `health/serializers.py` and
   `health/views.py`.
5. Export `api_v1_urlpatterns` from `health/urls.py` and register them from `afrourban/urls.py`.
6. Update `afrourban/api_schema.py` so `/api/v1/health/` is classified as public.
7. Regenerate committed OpenAPI artifacts if the repo continues to store them in `docs/api/`.

## Validation Commands

```bash
poetry run ruff check .
poetry run mypy .
poetry run pytest
poetry run python manage.py spectacular --file /tmp/openapi-health-validate.yaml --validate
```

## Latest Validation Results

- `poetry run ruff check .` -> passed
- `poetry run mypy .` -> `Success: no issues found in 79 source files`
- `poetry run pytest` -> `112 passed in 1.46s`
- `poetry run python manage.py spectacular --file /tmp/openapi-health-validate.yaml --validate`
  -> completed with `0` errors and `2` operationId-collision warnings resolved by
  drf-spectacular numeral suffixes for pre-existing admin route name overlap

## Published Artifacts

- Regenerated `docs/api/openapi-public.yaml` with `GET /api/v1/health/`
- Regenerated `docs/api/openapi-internal.yaml` with `GET /api/v1/health/`
- Refreshed `docs/api/endpoints.md` and `docs/api/README.md` for the final
  health-endpoint contract and release checks

## Manual Verification

### 1. Anonymous Health Check

- `GET /api/v1/health/` without credentials returns `200` and `{"status":"healthy"}` when the
  application is serving requests normally.

### 2. Non-Healthy Contract

- When the health evaluation service reports the application cannot handle requests normally,
  `GET /api/v1/health/` returns `503` and `{"status":"unhealthy"}`.

### 3. Public Documentation Visibility

- Public schema/UI includes `/api/v1/health/`.
- Internal schema/UI also includes `/api/v1/health/`.

### 4. Scope Guardrail

- The endpoint does not perform database or third-party dependency checks.
- Repeated health-check requests are not throttled.

## Expected Output Artifacts

- New `health/` Django app with service, serializer, view, route, and tests
- Updated [`afrourban/urls.py`](/Users/ernestjumbe/Documents/Projects/afrourban/afrourban/urls.py)
  and [`afrourban/api_schema.py`](/Users/ernestjumbe/Documents/Projects/afrourban/afrourban/api_schema.py)
- Updated OpenAPI artifacts in `docs/api/`
- Passing test, schema, lint, and type-check quality gates
