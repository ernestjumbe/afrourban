# Research: Username Registration and Email Privacy

**Feature**: 006-add-username-privacy  
**Date**: 2026-03-28

## 1. Custom User Schema Strategy

### Decision

Extend `CustomUser` with:

- `username` (stored string attribute)
- `username_changed_at` (nullable timestamp of most recent successful username change)

Keep `USERNAME_FIELD = "email"` so authentication remains email/password based.

### Rationale

This directly satisfies username persistence requirements while preserving existing authentication
behavior and token flows.

### Alternatives considered

- Switch login identifier from email to username: rejected because the feature explicitly requires
  continued email/password authentication.
- Store username in `Profile` instead of `CustomUser`: rejected because username is an account
  identity attribute and must be available consistently across auth/admin APIs.

## 2. Existing-User Backfill Policy

### Decision

Perform data backfill only for users with missing/blank usernames. For those users, set username to
that user's current email value. Preserve any non-empty existing username unchanged.

### Rationale

Matches clarification decisions and avoids overwriting established identities.

### Alternatives considered

- Overwrite all usernames with email: rejected by clarification.
- Skip automatic backfill and require manual remediation: rejected due to operational burden and
  migration risk.

## 3. Username Validation and Uniqueness Boundaries

### Decision

Enforce user-facing validation for registration and username-change operations:

- Allowed characters: letters, numbers, underscore (`_`), dot (`.`)
- Length: 3-30
- Must not start with `.`
- Must include at least one letter
- Case-insensitive uniqueness across all accounts

### Rationale

This reflects clarified UX and identity constraints while preventing ambiguous duplicates.

### Alternatives considered

- Case-sensitive uniqueness: rejected due to identity confusion risk.
- Looser free-form username policy: rejected due to moderation/support complexity.

## 4. Username Change and Cooldown Model

### Decision

Add authenticated username-change capability via API with cooldown enforcement:

- Default cooldown: 7 days
- Configurable via setting in whole days (`USERS_USERNAME_CHANGE_COOLDOWN_DAYS`)
- Cooldown applies only after successful username changes
- Cooldown does not apply after initial username creation or migration backfill

### Rationale

Satisfies clarified requirements and creates predictable anti-churn protection.

### Alternatives considered

- Immutable username after registration: rejected by clarification.
- Admin-only username changes: rejected because users must self-manage.

## 5. API Endpoint Contract for Username Change

### Decision

Introduce a dedicated authenticated endpoint under `/api/v1/auth/` for username changes, registered
via `users.urls.api_v1_urlpatterns` and included through main `api_urlpatterns`.

### Rationale

A dedicated endpoint isolates validation/cooldown semantics from unrelated profile updates and keeps
API contracts explicit.

### Alternatives considered

- Piggyback username update on profile PATCH endpoint: rejected because username is account identity,
  not profile metadata.
- No API endpoint (admin-only DB update): rejected as non-user-operable.

## 6. Email Visibility Enforcement Strategy

### Decision

Adopt an ownership/role-aware projection rule for serialized user objects:

- Owned user objects: email allowed
- Non-owned objects for non-privileged users: email omitted
- Authorized admin/staff endpoints: non-owned email allowed

Apply the rule consistently across detail/list/nested payloads and document in OpenAPI schema
examples/serializer behavior.

### Rationale

Directly enforces privacy requirements while preserving operational visibility for staff workflows.

### Alternatives considered

- Always hide non-owned emails for everyone, including staff: rejected by clarification.
- Endpoint-by-endpoint ad hoc behavior without shared rule: rejected due to drift/regression risk.

## 7. Observability and Test Strategy

### Decision

Add structured logging and tests for:

- Registration username validation outcomes
- Username change success/failure (`cooldown_active`, `username_taken`, `invalid_format`)
- Email redaction decisions in non-owned contexts
- Migration backfill outcomes

### Rationale

This supports constitution mandates for observability and test-first confidence.

### Alternatives considered

- No dedicated events/tests beyond happy path: rejected as insufficient for privacy-sensitive logic.
