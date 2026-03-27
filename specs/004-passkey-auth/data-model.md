# Data Model: Passkey Registration & Authentication

**Feature**: 004-passkey-auth  
**Date**: 2026-03-27

## Entity: WebAuthnCredential

Represents a single WebAuthn passkey credential registered by a user.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | BigAutoField | PK | Internal database identifier |
| `user` | ForeignKey → CustomUser | NOT NULL, on_delete=CASCADE, related_name="webauthn_credentials" | Owning user account |
| `credential_id` | BinaryField | NOT NULL, UNIQUE, max_length=1024 | WebAuthn credential identifier (opaque bytes from authenticator) |
| `public_key` | BinaryField | NOT NULL, max_length=1024 | COSE-encoded public key for signature verification |
| `sign_count` | PositiveIntegerField | NOT NULL, default=0 | Signature counter for cloning detection |
| `webauthn_user_id` | BinaryField | NOT NULL, max_length=64 | Random user handle used during registration (NOT the DB PK) |
| `device_label` | CharField | max_length=100, blank=True, default="" | User-provided or auto-generated device label |
| `is_enabled` | BooleanField | NOT NULL, default=True | False when disabled (e.g., cloning detected) |
| `created_at` | DateTimeField | auto_now_add=True | When the credential was registered |

### Indexes

| Index | Fields | Purpose |
|-------|--------|---------|
| Unique | `credential_id` | Fast lookup during authentication assertion |
| Composite | `user`, `is_enabled` | Efficient query for user's active credentials |

### Relationships

- **CustomUser → WebAuthnCredential**: One-to-many. A user may have 0–5 credentials. Enforced at the service layer (not DB constraint).
- **Cascade delete**: When a user is deleted, all their credentials are deleted.

### Validation Rules

| Rule | Enforcement Layer | Description |
|------|-------------------|-------------|
| Max 5 credentials per user | Service | `passkey_credential_add()` checks count before creating |
| `credential_id` globally unique | DB (unique constraint) | No two users can share the same credential ID |
| `sign_count` monotonically increasing | Service | Validated during authentication; credential disabled if violated |
| `is_enabled` must be True for auth | Service | Disabled credentials rejected during authentication |

### State Transitions

```text
                  ┌─────────┐
                  │ ENABLED │ ← Created during registration
                  └────┬────┘
                       │
          sign_count violation detected
                       │
                       ▼
                  ┌──────────┐
                  │ DISABLED │ ← Cannot authenticate
                  └────┬─────┘
                       │
               user removes credential
                       │
                       ▼
                  ┌─────────┐
                  │ DELETED │
                  └─────────┘
```

## Entity: CustomUser (existing — extended behaviour)

No new fields added to `CustomUser`. Passkey support is achieved through the `WebAuthnCredential` relationship and service-layer logic.

### Behavioural changes

| Behaviour | Before | After |
|-----------|--------|-------|
| Registration | email + password required | email + password OR email + passkey |
| Authentication | email + password only | email + password OR passkey (discoverable) |
| `has_usable_password()` | Always True | False for passkey-only users |
| Last auth method removal | N/A | Prevented if passkey is last method and no password set |

## Cache: WebAuthn Challenge

Ephemeral challenge data stored in Django cache (not a model).

| Key pattern | Value | TTL |
|-------------|-------|-----|
| `webauthn_challenge:{uuid}` | JSON: `{ "challenge": "<base64url>", "email": "<str or null>", "ceremony": "registration\|authentication" }` | 300s (configurable) |

Challenge is consumed (deleted from cache) upon successful verification. Expired challenges are removed naturally by cache TTL.
