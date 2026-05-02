# API Endpoint Inventory and Permission Matrix

Canonical API version: `/api/v1/`

This inventory is the release source of truth for active API operations and
their documentation visibility.

| Method | Path | Access Scope | Required Access | Public Docs | Internal Docs |
|---|---|---|---|---|---|
| POST | `/api/v1/auth/register/` | public | none | yes | yes |
| POST | `/api/v1/auth/token/` | public | none | yes | yes |
| POST | `/api/v1/auth/token/refresh/` | public | none | yes | yes |
| POST | `/api/v1/auth/token/verify/` | public | none | yes | yes |
| POST | `/api/v1/auth/email-verification/verify/` | public | none | yes | yes |
| POST | `/api/v1/auth/email-verification/resend/` | public | none | yes | yes |
| POST | `/api/v1/auth/password/reset/` | public | none | yes | yes |
| POST | `/api/v1/auth/password/reset/confirm/` | public | none | yes | yes |
| POST | `/api/v1/auth/passkey/register/options/` | public | none | yes | yes |
| POST | `/api/v1/auth/passkey/register/complete/` | public | none | yes | yes |
| POST | `/api/v1/auth/passkey/authenticate/options/` | public | none | yes | yes |
| POST | `/api/v1/auth/passkey/authenticate/complete/` | public | none | yes | yes |
| GET | `/api/v1/health/` | public | none | yes | yes |
| POST | `/api/v1/auth/logout/` | authenticated | authenticated user | no | yes |
| POST | `/api/v1/auth/password/change/` | authenticated | authenticated user | no | yes |
| PATCH | `/api/v1/auth/username/` | authenticated | authenticated user | no | yes |
| POST | `/api/v1/auth/passkey/add/options/` | authenticated | authenticated user | no | yes |
| POST | `/api/v1/auth/passkey/add/complete/` | authenticated | authenticated user | no | yes |
| GET | `/api/v1/auth/passkey/` | authenticated | authenticated user | no | yes |
| DELETE | `/api/v1/auth/passkey/{credential_id}/` | authenticated | authenticated user | no | yes |
| POST | `/api/v1/events/` | authenticated | authenticated user | no | yes |
| GET | `/api/v1/events/{event_id}/` | authenticated | authenticated user | no | yes |
| PATCH | `/api/v1/events/{event_id}/` | authenticated | personal owner or organization owner | no | yes |
| POST | `/api/v1/events/{event_id}/cover/` | authenticated | personal owner or organization owner | no | yes |
| DELETE | `/api/v1/events/{event_id}/cover/` | authenticated | personal owner or organization owner | no | yes |
| GET | `/api/v1/profiles/me/` | authenticated | authenticated user | no | yes |
| PATCH | `/api/v1/profiles/me/` | authenticated | authenticated user | no | yes |
| POST | `/api/v1/profiles/me/avatar/` | authenticated | authenticated user | no | yes |
| DELETE | `/api/v1/profiles/me/avatar/` | authenticated | authenticated user | no | yes |
| GET | `/api/v1/profiles/policies/{policy_id}/check/` | authenticated | authenticated user | no | yes |
| GET | `/api/v1/profiles/{user_id}/` | authenticated | authenticated user | no | yes |
| GET | `/api/v1/admin/users/` | staff | staff user | no | yes |
| GET | `/api/v1/admin/users/{user_id}/` | staff | staff user | no | yes |
| PATCH | `/api/v1/admin/users/{user_id}/` | staff | staff user | no | yes |
| POST | `/api/v1/admin/users/{user_id}/activate/` | staff | staff user | no | yes |
| POST | `/api/v1/admin/users/{user_id}/deactivate/` | staff | staff user | no | yes |
| GET | `/api/v1/admin/users/{user_id}/permissions/` | staff | staff user | no | yes |
| PUT | `/api/v1/admin/users/{user_id}/permissions/` | staff | staff user | no | yes |
| GET | `/api/v1/admin/users/roles/` | staff | staff user | no | yes |
| POST | `/api/v1/admin/users/roles/` | staff | staff user | no | yes |
| GET | `/api/v1/admin/users/roles/{role_id}/` | staff | staff user | no | yes |
| PATCH | `/api/v1/admin/users/roles/{role_id}/` | staff | staff user | no | yes |
| DELETE | `/api/v1/admin/users/roles/{role_id}/` | staff | staff user | no | yes |

## Documentation Endpoints

| Endpoint | Access |
|---|---|
| `/api/v1/docs/public/schema/` | AllowAny |
| `/api/v1/docs/public/` | AllowAny |
| `/api/v1/docs/internal/schema/` | IsAuthenticated |
| `/api/v1/docs/internal/` | IsAuthenticated |

## Registration Contract Notes

`POST /api/v1/auth/register/` now requires `username` in addition to
`email`, `password`, and `password_confirm`.

- Username must be 3-30 characters.
- Username must include at least one letter.
- Username cannot start with `.`.
- Username may contain only letters, numbers, `_`, and `.`.
- Username uniqueness is enforced case-insensitively.
- Authentication remains `POST /api/v1/auth/token/` with `email` and
  `password`; username is not a login credential.

## Email Visibility Notes

- `POST /api/v1/auth/register/` returns the created user's email.
- `GET /api/v1/profiles/me/` returns the authenticated user's email.
- `GET /api/v1/profiles/{user_id}/` includes `email` only when the
  requested profile is owned by the authenticated user.
- Non-owned profile payloads omit `email` for non-privileged users.
- Authorized staff/admin endpoints under `/api/v1/admin/users/` retain
  non-owned email visibility.

## Username Change Notes

- `PATCH /api/v1/auth/username/` is available to authenticated users.
- Username changes use the same format and case-insensitive uniqueness rules
  as registration.
- The first post-registration username change is allowed immediately.
- After a successful change, the user enters a cooldown window.
- The default cooldown is 7 days and can be overridden with
  `USERS_USERNAME_CHANGE_COOLDOWN_DAYS`.
- Cooldown failures return a `cooldown_active` problem-details code and include
  the next allowed timestamp in the response detail.

## Published Schema Notes

- `docs/api/openapi-public.yaml` excludes authenticated and staff-only routes,
  including `PATCH /api/v1/auth/username/`.
- `docs/api/openapi-internal.yaml` includes the username-change endpoint and the
  internal `x-deprecations` metadata extension.

## Application Health Endpoint Notes

- `GET /api/v1/health/` is a public route intended for monitoring systems and
  frontend startup checks.
- The endpoint accepts requests with or without credentials and returns the
  same machine-readable payload shape either way.
- Healthy responses return HTTP `200` with `{"status":"healthy"}`.
- Non-healthy responses return HTTP `503` with `{"status":"unhealthy"}`.
- The endpoint reports only application-process health; database, cache, third-
  party API, and other external dependency checks are out of scope.
- External dependency failures alone do not change the reported health status
  while the application process can still handle requests normally.
- Response bodies stay status-only and do not expose dependency names,
  diagnostics, or internal failure details.
- The committed `docs/api/openapi-public.yaml` and
  `docs/api/openapi-internal.yaml` artifacts both publish the same status-only
  contract for `/api/v1/health/`.
- Each request emits one structured `health_check_evaluated` event with the
  outcome, HTTP status, request method, path, and nullable request user ID.
- The endpoint appears in both `docs/api/openapi-public.yaml` and
  `docs/api/openapi-internal.yaml`.

## Organization Profiles

- Namespace: `/api/v1/organizations/`
- Auth scope: all organizations endpoints are authenticated in `v1`
- Active routes:
  `GET`/`POST /api/v1/organizations/`,
  `GET`/`PATCH /api/v1/organizations/{organization_id}/`,
  `POST`/`DELETE /api/v1/organizations/{organization_id}/logo/`, and
  `POST`/`DELETE /api/v1/organizations/{organization_id}/cover/`
- Collection reads return the standard pagination envelope with `count`, `next`,
  `previous`, and `results`
- Supported collection query parameters:
  `owner_scope=all|mine`,
  `organization_type=<choice>`,
  `is_online_only=true|false`,
  `search=<fragment>`,
  `ordering=name|-name|created_at|-created_at`,
  `page`,
  and `page_size` (clamped to `100`)
- Collection and detail payloads expose organization-only fields:
  `id`, `owner_id`, `name`, `description`, `organization_type`,
  `is_online_only`, `physical_address`, `logo_url`, `cover_image_url`,
  `created_at`, and `updated_at`
- Online-only organizations always return `physical_address: null`
- Metadata writes and branding mutations are owner-only; non-owner attempts
  return `403` Problem Details responses
- Organizations endpoints appear in the internal schema only and remain absent
  from the public schema because all reads and writes require authentication

## Events App

- Namespace: `/api/v1/events/`
- Auth scope: all events endpoints are authenticated in `v1`
- Active routes:
  `POST /api/v1/events/`,
  `GET`/`PATCH /api/v1/events/{event_id}/`, and
  `POST`/`DELETE /api/v1/events/{event_id}/cover/`
- Create requests support both personal events and organization-owned events
  when the authenticated actor owns the selected organization
- Detail reads are available to any authenticated viewer
- Metadata writes are limited to the personal event owner or the current owner
  of the event's organization
- Successful updates to `title`, `start_at`, `end_at`, and `location` create
  immutable audit rows; organizer context remains immutable after creation
- Cover-image uploads accept JPEG, PNG, and WebP files up to 5MB and follow the
  same write-permission rules as metadata updates
- Events endpoints appear in the internal schema only and remain absent from
  the public schema because all reads and writes require authentication
