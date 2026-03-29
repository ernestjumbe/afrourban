# API Verification Runbook

This runbook defines release checks for API routing, documentation visibility,
and deprecation governance.

## Prerequisites

- Python 3.11+
- Poetry environment installed
- Database migrated for the active settings module

## 1. Route Contract Verification

Run route contract and compatibility tests:

```bash
poetry run pytest \
  users/tests/test_api_versioning.py \
  profiles/tests/test_api_versioning.py \
  users/tests/test_email_verification.py -q
```

Expected result:

- All tests pass.
- Legacy unversioned `/api/auth/*`, `/api/admin/users/*`, `/api/profiles/*` routes return `404`.
- Canonical `/api/v1/` endpoints resolve.

## 2. Documentation Visibility Verification

Run documentation contract tests:

```bash
poetry run pytest \
  users/tests/test_api_docs.py \
  profiles/tests/test_api_docs.py -q
```

Expected result:

- Public schema includes only public endpoints.
- Internal schema includes all active endpoints.
- Internal docs and internal schema require authentication.

## 3. Deprecation Policy Verification

Validate deprecation rules and registry:

```bash
poetry run pytest users/tests/test_api_deprecations.py -q
poetry run python manage.py validate_api_deprecations --settings=afrourban.settings.test
```

Expected result:

- 90-day minimum notice rule is enforced.
- Deprecated entries require `deprecation_date`, `removal_date`, and `migration_path`.
- Registry validation command exits successfully.

## 4. OpenAPI Generation and Validation

Validate generated schema:

```bash
poetry run python manage.py spectacular \
  --settings=afrourban.settings.test \
  --validate \
  --file /tmp/openapi-validate.yaml
```

Regenerate checked-in artifacts:

```bash
poetry run python - <<'PY'
import os
from pathlib import Path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'afrourban.settings.test')
import django
django.setup()
from rest_framework.test import APIRequestFactory, force_authenticate
from afrourban.api_schema import InternalSchemaAPIView, PublicSchemaAPIView

out_dir = Path('docs/api')
out_dir.mkdir(parents=True, exist_ok=True)
factory = APIRequestFactory()

public_request = factory.get('/api/v1/docs/public/schema/')
public_response = PublicSchemaAPIView.as_view()(public_request)
public_response.render()

class _SchemaUser:
    is_authenticated = True
    is_active = True
    is_staff = True

internal_request = factory.get('/api/v1/docs/internal/schema/')
force_authenticate(internal_request, user=_SchemaUser())
internal_response = InternalSchemaAPIView.as_view()(internal_request)
internal_response.render()

(out_dir / 'openapi-public.yaml').write_bytes(public_response.content)
(out_dir / 'openapi-internal.yaml').write_bytes(internal_response.content)
PY
```

Expected result:

- `docs/api/openapi-public.yaml` excludes authenticated/staff routes.
- `docs/api/openapi-internal.yaml` includes all active routes and `x-deprecations`.
- Internal artifacts include `PATCH /api/v1/auth/username/`; public artifacts do not.

## 5. Quality Gates

Run repository quality gates:

```bash
poetry run ruff check .
poetry run mypy .
poetry run pytest -q
```

If any gate fails:

1. Record failing command and output.
2. Document whether failure is pre-existing or introduced by the current change.
3. Add remediation plan and owner before release.

## 6. Feature 006 Release Checks

Run the feature-specific contract coverage:

```bash
poetry run pytest \
  users/tests/test_registration.py \
  users/tests/test_username_change.py \
  users/tests/test_api_email_visibility.py \
  users/tests/test_migrations_username_backfill.py \
  profiles/tests/test_api_email_visibility.py -q
```

Expected result:

- Registration requires `username` and preserves email/password login.
- Username changes obey validation, case-insensitive uniqueness, and cooldown rules.
- Backfill tests confirm only missing usernames are populated and no
  `username_changed_at` values are introduced by migration.
- Non-owned emails remain hidden for non-privileged users while authorized
  staff/admin flows retain allowed access.

Compatibility check for this release:

- `/api/v1/` remains the canonical namespace.
- `POST /api/v1/auth/token/` still authenticates with `email` and `password`.
- No version or endpoint deprecation entry is introduced by feature 006.
