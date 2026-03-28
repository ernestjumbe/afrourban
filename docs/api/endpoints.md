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
