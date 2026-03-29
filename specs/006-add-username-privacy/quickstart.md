# Quickstart: Username Registration and Email Privacy

**Feature**: 006-add-username-privacy  
**Branch**: `006-add-username-privacy`

## Prerequisites

- Python 3.11+
- Poetry installed
- Database available and migrations up to date
- Feature branch checked out

## Setup

```bash
git checkout 006-add-username-privacy
poetry install
```

## Implementation Order (Test-First)

### 1. Write failing tests first

```bash
# Suggested focused test modules
poetry run pytest users/tests/test_registration.py -q
poetry run pytest users/tests/test_username_change.py -q
poetry run pytest users/tests/test_api_email_visibility.py -q
poetry run pytest users/tests/test_migrations_username_backfill.py -q
poetry run pytest profiles/tests/test_api_email_visibility.py -q
```

Coverage targets for this feature:

- Username required in registration
- Username format and case-insensitive uniqueness
- Existing-user backfill only for missing/blank usernames
- Username change endpoint behavior (success, duplicate, invalid, cooldown active)
- Cooldown default/config behavior and no initial-creation cooldown
- Email omission in non-owned user objects for non-privileged users
- Email visibility preserved for authorized admin/staff operations

### 2. Implement data model and migration

- Extend `users.CustomUser` with username-related fields.
- Create schema + data migrations for backfill rules.
- Keep email as login field.

```bash
poetry run python manage.py makemigrations users
poetry run python manage.py migrate
```

### 3. Implement service/selector/serializer/view changes

- Update registration input/output and creation service.
- Add username-change service + endpoint with cooldown logic.
- Add/adjust projection rules for ownership/role-based email visibility.
- Wire route in `users.urls` under `/api/v1/auth/`.
- Regenerate/refresh API docs artifacts.

### 4. Run full validation gates

```bash
poetry run ruff check .
poetry run mypy .
poetry run pytest -q
poetry run python manage.py spectacular --settings=afrourban.settings.test --validate --file /tmp/openapi-006-validate.yaml
```

## Manual Verification Checklist

### Registration and Login

1. `POST /api/v1/auth/register/` without `username` fails with validation error.
2. `POST /api/v1/auth/register/` with valid `username` succeeds.
3. `POST /api/v1/auth/token/` still authenticates using `email` + `password`.

### Username Change and Cooldown

1. First successful username change after creation is allowed.
2. Immediate second change is blocked while cooldown is active.
3. Change becomes allowed after cooldown duration.
4. Invalid/duplicate username changes are rejected.

### Email Privacy

1. Owned user objects include email where allowed.
2. Non-owned user objects in non-privileged contexts omit email.
3. Authorized admin/staff operations can still include non-owned emails.

### Username Rollout and Backfill

1. Before rollout, identify users with `NULL`, empty, or whitespace-only usernames.
2. After rollout, verify no user account remains without a username.
3. Verify existing non-empty usernames remain unchanged after the migration.
4. If an email-derived username conflicts case-insensitively with an existing username, expect the stored fallback format `email__legacy_<user_id>`.
5. Confirm backfilled users do not receive `username_changed_at` values from the rollout migration.

### Documentation

1. OpenAPI schema includes required `username` on registration.
2. Schema/docs include username-change endpoint and cooldown behavior.
3. Documentation still reflects `/api/v1/` namespace and route registration architecture.

## Compatibility & Deprecation Note

- This feature is an additive `/api/v1/` release.
- `POST /api/v1/auth/token/` remains email/password based.
- `PATCH /api/v1/auth/username/` is new and does not replace an existing route.
- No version or endpoint deprecation entry is introduced by this feature.

## Validation Capture

Captured on 2026-03-28 after Phase 7 completion:

- `poetry run ruff check .` -> passed
- `poetry run mypy .` -> `Success: no issues found in 67 source files`
- `poetry run pytest -q` -> `95 passed in 1.14s`
- `poetry run python manage.py spectacular --settings=afrourban.settings.test --validate --file /tmp/openapi-006-validate.yaml` -> passed with 0 schema errors and 2 existing `operationId` collision warnings for admin list/detail routes
- `poetry run python manage.py validate_api_deprecations --settings=afrourban.settings.test` -> deprecation registry valid
- Regenerated publication artifacts: `docs/api/openapi-public.yaml` and `docs/api/openapi-internal.yaml`

## Expected Artifacts

- Updated user model/migrations with username support
- Username change endpoint under `/api/v1/auth/`
- Ownership/role-based email-visibility enforcement
- Updated OpenAPI docs and endpoint references
- Passing quality gates (`ruff`, `mypy`, `pytest`, `spectacular --validate`)
