# Username and Email Privacy API Contract

**Feature**: 006-add-username-privacy  
**Date**: 2026-03-28

## 1. Namespace and Routing Contract

1. All changed and added routes remain under `/api/v1/`.
2. Any new auth route for username change MUST be registered in `users.urls.api_v1_urlpatterns`.
3. Main `afrourban/urls.py` MUST continue including routes through `api_urlpatterns` under `/api/`.
4. OpenAPI documentation MUST be regenerated with drf-spectacular (OpenAPI 3.0+).

## 2. Registration Contract

### Endpoint

- `POST /api/v1/auth/register/`

### Request Body

| Field | Required | Rules |
|-------|----------|-------|
| `email` | yes | valid email |
| `password` | yes | existing password policy |
| `password_confirm` | yes | matches password |
| `username` | yes | allowed chars: letters, digits, `_`, `.`; 3-30 length; cannot start `.`; must include at least one letter |
| `display_name` | no | optional |

### Behavior

- Registration fails when username is missing/invalid.
- Registration fails when username already exists (case-insensitive collision).
- Successful registration persists the supplied username on the created user.
- Successful registration still authenticates later via email/password.

### Success Response Contract

| Field | Description |
|-------|-------------|
| `id` | Created user id |
| `email` | Created user email |
| `profile` | Created profile payload |
| `created_at` | Registration timestamp |

### Authentication Compatibility

- `POST /api/v1/auth/token/` continues to accept `email` + `password`.
- Username is an account attribute, not an authentication credential.

## 3. Username Change Contract

### Endpoint

- `PATCH /api/v1/auth/username/` (authenticated)

### Request Body

| Field | Required | Rules |
|-------|----------|-------|
| `username` | yes | same validation + case-insensitive uniqueness as registration |

### Success Response Contract

| Field | Description |
|-------|-------------|
| `id` | Authenticated user id |
| `username` | Updated username |
| `cooldown_days` | Cooldown duration in days that now applies |
| `next_allowed_at` | Earliest timestamp for next allowed username change (ISO 8601) |

### Failure Contract

| Condition | Expected Outcome |
|-----------|------------------|
| Invalid username format | Validation error on `username` |
| Username already taken (case-insensitive) | Validation error on `username` |
| Cooldown active | Problem-details validation response with `code = "cooldown_active"` and `detail` containing the next allowed timestamp |

### Cooldown Rules

- Default cooldown is 7 days.
- Cooldown duration is configurable via settings in whole days.
- Cooldown applies only after successful username changes.
- Cooldown does not apply after initial username creation or migration backfill.
- Successful responses always include the applied `cooldown_days` value and the
  computed `next_allowed_at` timestamp.

## 4. Email Visibility Contract

### Rule Matrix

| Request Context | Subject User Ownership | Email in Response Object |
|----------------|------------------------|--------------------------|
| Non-privileged authenticated request | Owned object | Allowed |
| Non-privileged authenticated request | Non-owned object | Forbidden |
| Authorized admin/staff operation | Non-owned object | Allowed |

### Scope

- Rule applies to any API response body containing user objects (list/detail/nested).
- Privacy rule must be enforced consistently by serializers/projection helpers.

### Endpoint Examples

- `GET /api/v1/profiles/me/` includes `email` for the authenticated owner.
- `GET /api/v1/profiles/{user_id}/` omits `email` for non-owned profiles and
  includes it only when the requester owns the profile.
- `GET /api/v1/admin/users/` and `GET /api/v1/admin/users/{user_id}/` may
  include non-owned emails for authorized staff/admin operations.

## 5. Documentation Contract

1. Schema examples and endpoint docs must show `username` as required registration input.
2. Schema/docs must include username-change endpoint and cooldown behavior.
3. Schema/docs must describe ownership/role-based email visibility behavior.
4. Public/internal documentation visibility split remains intact with this feature.

## 6. Compatibility & Deprecation

- Existing `/api/v1/auth/token/` contract remains email/password based.
- No version deprecation is introduced by this feature.
- If a future endpoint contract is deprecated, deprecation metadata must include date, removal date, and migration path.
