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
| POST | `/api/v1/auth/logout/` | authenticated | authenticated user | no | yes |
| POST | `/api/v1/auth/password/change/` | authenticated | authenticated user | no | yes |
| PATCH | `/api/v1/auth/username/` | authenticated | authenticated user | no | yes |
| POST | `/api/v1/auth/passkey/add/options/` | authenticated | authenticated user | no | yes |
| POST | `/api/v1/auth/passkey/add/complete/` | authenticated | authenticated user | no | yes |
| GET | `/api/v1/auth/passkey/` | authenticated | authenticated user | no | yes |
| DELETE | `/api/v1/auth/passkey/{credential_id}/` | authenticated | authenticated user | no | yes |
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
