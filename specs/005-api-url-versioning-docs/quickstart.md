# Quickstart: API URL Versioning and Documentation

**Feature**: 005-api-url-versioning-docs  
**Branch**: `005-api-url-versioning-docs`

## Prerequisites

- Python 3.11+
- Poetry installed
- Existing `users` and `profiles` APIs available locally
- Database migrated

## Setup

```bash
# Ensure feature branch
git checkout 005-api-url-versioning-docs

# Add API schema tooling
poetry add drf-spectacular
```

## Configuration

Update `afrourban/settings/base.py`:

- Add `drf_spectacular` to `INSTALLED_APPS`
- Set DRF schema class to `drf_spectacular.openapi.AutoSchema`
- Configure `SPECTACULAR_SETTINGS` for title/version and split-schema generation hooks

## Routing Migration

1. In `afrourban/urls.py`, define `api_urlpatterns` in main URL config.
2. Register all API groups under versioned prefixes (`v1/auth/`, `v1/admin/users/`, `v1/profiles/`).
3. Include `api_urlpatterns` under `/api/`.
4. Remove unversioned legacy route includes.
5. Add docs routes:
   - `/api/v1/docs/public/schema/`
   - `/api/v1/docs/public/`
   - `/api/v1/docs/internal/schema/`
   - `/api/v1/docs/internal/`

## Validation Checklist

```bash
# Lint and type checks
poetry run ruff check .
poetry run mypy .

# Test suite
poetry run pytest

# OpenAPI schema validation (constitution requirement)
poetry run python manage.py spectacular --file schema.yaml --validate
```

## Manual Verification

### 1. Versioned routes respond

- `POST /api/v1/auth/register/`
- `GET /api/v1/profiles/me/` (authenticated)
- `GET /api/v1/admin/users/` (staff)

### 2. Legacy unversioned routes are unavailable

- `POST /api/auth/register/` returns unsupported-route error
- `GET /api/profiles/me/` returns unsupported-route error

### 3. Documentation visibility split

- Public docs show only public endpoints
- Internal docs (authenticated) show full endpoint inventory including staff/admin routes

### 4. Deprecation policy validation

- Future deprecations include `deprecation_date`, `removal_date`, and `migration_path`
- Removal date is at least 90 days after deprecation date

## Expected Output Artifacts

- Updated URL routing with `/api/v1/` namespace
- drf-spectacular schema generation configured
- Public/internal documentation views available
- Route inventory and schema tests passing

## Validation Run Record (2026-03-28)

### Quickstart Workflow Validation (T035)

Executed commands:

```bash
poetry run pytest \
  users/tests/test_api_deprecations.py \
  users/tests/test_api_docs.py \
  profiles/tests/test_api_docs.py -q

poetry run python manage.py validate_api_deprecations --settings=afrourban.settings.test
```

Observed outcomes:

- `9 passed in 0.44s` for deprecation/docs validation tests.
- `Deprecation registry is valid: .../docs/api/deprecations.yaml`.

Artifact verification:

```text
docs/api/openapi-public.yaml
  path_count=12
  has_admin_users=False
  has_logout=False
  has_x_deprecations=False
docs/api/openapi-internal.yaml
  path_count=29
  has_admin_users=True
  has_logout=True
  has_x_deprecations=True
```

### Full Quality Gates (T036)

Executed commands:

```bash
poetry run ruff check .
poetry run mypy .
poetry run pytest -q
poetry run python manage.py spectacular --settings=afrourban.settings.test --validate --file /tmp/openapi-full-validate.yaml
```

Observed outcomes:

- `ruff check .` FAILED with pre-existing issues (37 total), primarily:
  - star-import lint errors in `afrourban/settings/dev.py` and `afrourban/settings/local.py`
  - `F821` in `profiles/services.py` (`Policy` type reference)
  - `E402` late imports in `users/services.py`
- `mypy .` FAILED: `Command not found: mypy` in the current Poetry environment.
- `pytest -q` PASSED: `71 passed in 0.71s`.
- `spectacular --validate` PASSED with `Errors: 0`, plus existing operationId collision warnings:
  - `admin_users_retrieve`
  - `admin_users_roles_retrieve`

Remediation notes:

1. Add/restore `mypy` in the active Poetry environment before enforcing a mypy gate.
2. Resolve existing Ruff findings in settings/services modules, or scope lint commands in CI to agreed targets.
3. Add explicit operation IDs (or schema annotations) for colliding admin endpoints to remove spectacular warnings.
