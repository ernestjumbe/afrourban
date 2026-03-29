# Data Model: Username Registration and Email Privacy

**Feature**: 006-add-username-privacy  
**Date**: 2026-03-28

This feature extends existing account identity data and introduces explicit projection/cooldown
rules. Entities are conceptual and map to Django model fields, serializers, and settings.

## Entity: UserAccount (Extended)

Represents authentication identity (`users.CustomUser`) with username lifecycle support.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | integer | primary key | User identifier |
| `email` | string | required, unique, case-insensitive | Login identifier |
| `username` | string | required, 3-30 chars for user-supplied values, globally case-insensitive unique | Account username |
| `username_changed_at` | datetime/null | nullable | Timestamp of last successful username change |
| `is_active` | boolean | required | Account enabled state |
| `is_staff` | boolean | required | Staff/admin capability |
| `is_email_verified` | boolean | required | Email verification state |
| `date_joined` | datetime | required | Account creation time |

### Validation Rules

- Authentication uses `email + password`; username is not a login credential.
- Registration requires username input.
- Username format for user-supplied values:
  - allowed: letters, digits, `_`, `.`
  - length 3-30
  - cannot start with `.`
  - must include at least one letter
- Username uniqueness is global and case-insensitive.
- Migration backfill sets username from email only for missing/blank usernames.

### State Transitions (Username Change Eligibility)

```text
EligibleForChange --(successful change)--> CooldownActive
CooldownActive --(cooldown elapsed)--> EligibleForChange
```

- Initial account creation starts in `EligibleForChange`.
- First user-initiated username change is never blocked by cooldown.
- Cooldown starts only after successful username change.

## Entity: UsernameChangePolicy

Represents configuration and computed cooldown behavior for username updates.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `cooldown_days` | integer | required, default 7, >= 0 | Global username-change lock period in whole days |
| `last_changed_at` | datetime/null | derived from `UserAccount.username_changed_at` | Last successful change timestamp |
| `next_allowed_at` | datetime/null | derived | Earliest allowed timestamp for next change |
| `is_change_allowed` | boolean | derived | Whether username change may proceed now |

### Validation Rules

- `cooldown_days` is read from application settings.
- If `last_changed_at` is null, change is allowed.
- If now < `next_allowed_at`, change is rejected with cooldown error.
- Changing `cooldown_days` affects subsequent eligibility checks without rewriting history.

## Entity: UserObjectProjection

Represents API response projection rules for user-related payloads.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `viewer_user_id` | integer | required | Authenticated requester ID |
| `subject_user_id` | integer | required | User object represented in payload |
| `viewer_role` | enum | required (`non_privileged`, `staff`) | Role category relevant to visibility |
| `is_owned` | boolean | derived (`viewer_user_id == subject_user_id`) | Ownership flag |
| `can_view_email` | boolean | derived | Whether email field is included |

### Visibility Rules

- If `is_owned=true`, `can_view_email=true`.
- If `is_owned=false` and `viewer_role=non_privileged`, `can_view_email=false`.
- If `is_owned=false` and request is an authorized staff/admin operation, `can_view_email=true`.
- Rules apply consistently across list, detail, and nested response objects.

## Entity: UsernameChangeRequest (API Input/Output)

Represents one username-change API interaction (service-layer command model).

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `username` | string | required, format-valid, case-insensitive unique | Requested new username |
| `changed_at` | datetime | set on success | Effective change timestamp |
| `cooldown_days` | integer | required | Applied cooldown configuration |
| `next_allowed_at` | datetime | derived on success | Next valid username-change time |

### Failure Modes

- `invalid_format`: requested username violates format rules.
- `username_taken`: requested username collides case-insensitively.
- `cooldown_active`: current time is before `next_allowed_at`.
