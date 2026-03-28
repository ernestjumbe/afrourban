# API Versioning and Documentation Contract

**Feature**: 005-api-url-versioning-docs  
**Date**: 2026-03-28

## 1. Namespace Contract

1. All active API operations MUST be reachable under `/api/v1/`.
2. Main `afrourban/urls.py` MUST define `api_urlpatterns` and include it under `/api/`.
3. Unversioned legacy routes (`/api/auth/*`, `/api/admin/users/*`, `/api/profiles/*`) MUST NOT be
   served after rollout.
4. Future breaking changes MUST be introduced in a new version namespace (for example `/api/v2/`).

## 2. Documentation Publication Contract

| View | Endpoint | Access | Coverage Rule |
|------|----------|--------|---------------|
| Public schema | `/api/v1/docs/public/schema/` | AllowAny | Only public endpoints |
| Public UI | `/api/v1/docs/public/` | AllowAny | Renders public schema |
| Internal schema | `/api/v1/docs/internal/schema/` | IsAuthenticated | All active endpoints |
| Internal UI | `/api/v1/docs/internal/` | IsAuthenticated | Renders internal schema |

## 3. Endpoint Inventory Contract (`/api/v1/`)

### 3.1 Public Endpoints (must appear in both public and internal docs)

| Method | Path | Permission Scope |
|--------|------|------------------|
| POST | `/api/v1/auth/register/` | public |
| POST | `/api/v1/auth/token/` | public |
| POST | `/api/v1/auth/token/refresh/` | public |
| POST | `/api/v1/auth/token/verify/` | public |
| POST | `/api/v1/auth/email-verification/verify/` | public |
| POST | `/api/v1/auth/email-verification/resend/` | public |
| POST | `/api/v1/auth/password/reset/` | public |
| POST | `/api/v1/auth/password/reset/confirm/` | public |
| POST | `/api/v1/auth/passkey/register/options/` | public |
| POST | `/api/v1/auth/passkey/register/complete/` | public |
| POST | `/api/v1/auth/passkey/authenticate/options/` | public |
| POST | `/api/v1/auth/passkey/authenticate/complete/` | public |

### 3.2 Authenticated Endpoints (must appear only in internal docs)

| Method | Path | Permission Scope |
|--------|------|------------------|
| POST | `/api/v1/auth/logout/` | authenticated |
| POST | `/api/v1/auth/password/change/` | authenticated |
| POST | `/api/v1/auth/passkey/add/options/` | authenticated |
| POST | `/api/v1/auth/passkey/add/complete/` | authenticated |
| GET | `/api/v1/auth/passkey/` | authenticated |
| DELETE | `/api/v1/auth/passkey/{credential_id}/` | authenticated |
| GET | `/api/v1/profiles/me/` | authenticated |
| PATCH | `/api/v1/profiles/me/` | authenticated |
| POST | `/api/v1/profiles/me/avatar/` | authenticated |
| DELETE | `/api/v1/profiles/me/avatar/` | authenticated |
| GET | `/api/v1/profiles/policies/{policy_id}/check/` | authenticated |
| GET | `/api/v1/profiles/{user_id}/` | authenticated |

### 3.3 Staff Endpoints (must appear only in internal docs)

| Method | Path | Permission Scope |
|--------|------|------------------|
| GET | `/api/v1/admin/users/` | staff |
| GET | `/api/v1/admin/users/{user_id}/` | staff |
| PATCH | `/api/v1/admin/users/{user_id}/` | staff |
| POST | `/api/v1/admin/users/{user_id}/activate/` | staff |
| POST | `/api/v1/admin/users/{user_id}/deactivate/` | staff |
| GET | `/api/v1/admin/users/{user_id}/permissions/` | staff |
| PUT | `/api/v1/admin/users/{user_id}/permissions/` | staff |
| GET | `/api/v1/admin/users/roles/` | staff |
| POST | `/api/v1/admin/users/roles/` | staff |
| GET | `/api/v1/admin/users/roles/{role_id}/` | staff |
| PATCH | `/api/v1/admin/users/roles/{role_id}/` | staff |
| DELETE | `/api/v1/admin/users/roles/{role_id}/` | staff |

## 4. Deprecation Policy Contract

For every future deprecated API version or endpoint, documentation MUST include:

- `deprecation_date` (ISO date)
- `removal_date` (ISO date)
- `migration_path` (specific upgrade guidance)

And MUST enforce:

- `removal_date >= deprecation_date + 90 days`

## 5. Compatibility Contract

- `/api/v1/` MUST preserve existing behavior and documented contract semantics.
- Additive backward-compatible response changes are allowed (for example optional fields).
- Breaking changes require a new namespace (`/api/v2/`).
