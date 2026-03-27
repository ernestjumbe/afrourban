# Data Model: Email Verification for User Registration

**Branch**: `003-email-verification-registration`  
**Phase**: 1 — Design

---

## Modified Entity: `CustomUser` (`users/models.py`)

### New Field

| Field | Type | Default | Constraints | Notes |
|-------|------|---------|-------------|-------|
| `is_email_verified` | `BooleanField` | `False` | Not null | Existing users set to `True` via data migration |

### Field Detail

```
is_email_verified
  Type:     BooleanField
  Default:  False
  DB index: None (queried only via the user object after authentication)
  Null:     Not null
  Purpose:  Primary login gate. If False, TokenObtainPairSerializer blocks
            token issuance with error code "email_not_verified".
```

### Migration Strategy

A single migration file (`0002_add_email_verification.py`) will:
1. Add `is_email_verified = BooleanField(default=False)` to `CustomUser`
2. Run `RunPython` to set `is_email_verified=True` for all pre-existing users (grandfather)
3. Add the `EmailVerificationToken` model

---

## New Entity: `EmailVerificationToken` (`users/models.py`)

### Fields

| Field | Type | Default | Constraints | Notes |
|-------|------|---------|-------------|-------|
| `id` | `BigAutoField` | Auto | PK | Django default |
| `user` | `OneToOneField → CustomUser` | — | `on_delete=CASCADE`, `related_name="email_verification_token"` | Each user has at most one token at a time |
| `token` | `CharField(max_length=64)` | — | `unique=True`, `db_index=True` | Generated via `secrets.token_urlsafe(32)` (43 chars) |
| `created_at` | `DateTimeField` | `auto_now_add=True` | Not null | Time of token issuance |
| `expires_at` | `DateTimeField` | — | Not null | `created_at + timedelta(days=app_settings.EMAIL_VERIFICATION_TOKEN_EXPIRY_DAYS)` |

### Notes

- **No `is_consumed` flag**: The token is deleted (not flagged) upon successful verification. Absence of the record means the token has been consumed. Expired tokens are also deleted at point of rejection.
- **Single active token invariant**: Enforced at the database level by `OneToOneField`. A resend deletes the existing token record and creates a new one.
- **Cascade deletion**: Deleting the related `CustomUser` (re-registration supersede path) automatically deletes the `EmailVerificationToken` via `CASCADE`.

---

## Relationships

```
CustomUser ──────────── EmailVerificationToken
  1                             0..1
  (OneToOneField, CASCADE)
  
CustomUser ──────────── Profile
  1                       1
  (OneToOneField, existing)
```

---

## App Settings (`users/conf.py`)

New module defining all configurable defaults for the users app. Values are overridable via the active project settings module.

| Setting Key | Type | Default | Purpose |
|-------------|------|---------|---------|
| `USERS_EMAIL_VERIFICATION_TOKEN_EXPIRY_DAYS` | `int` | `7` | Days until a verification token expires |
| `USERS_EMAIL_VERIFICATION_BASE_URL` | `str` | `""` | Base URL prepended to the verification link (e.g. `https://app.example.com`) |
| `USERS_EMAIL_VERIFICATION_FROM_EMAIL` | `str` | `settings.DEFAULT_FROM_EMAIL` | Sender address for verification emails |
| `USERS_EMAIL_VERIFICATION_SITE_NAME` | `str` | `"Afrourban"` | Site name used in email body copy |

### Access Pattern

All application code imports `app_settings` from `users.conf`:

```python
from users.conf import app_settings

expiry_days = app_settings.EMAIL_VERIFICATION_TOKEN_EXPIRY_DAYS
base_url = app_settings.EMAIL_VERIFICATION_BASE_URL
```

### Override Example (project `settings/local.py` or `settings/prd.py`)

```python
USERS_EMAIL_VERIFICATION_BASE_URL = "https://app.afrourban.com"
USERS_EMAIL_VERIFICATION_FROM_EMAIL = "noreply@afrourban.com"
USERS_EMAIL_VERIFICATION_TOKEN_EXPIRY_DAYS = 7
USERS_EMAIL_VERIFICATION_SITE_NAME = "Afrourban"
```

---

## State Transitions

### `CustomUser.is_email_verified`

```
[registered] ──── email_verification_verify(token) ───► [verified]
    │
    │ (login attempt while is_email_verified=False)
    ▼
[blocked from login — error code: email_not_verified]
```

### `EmailVerificationToken` Lifecycle

```
[user registers or resend requested]
        │
        ▼
[token created — expires_at = now + expiry_days]
        │
        ├──── user clicks link within expiry window ──► token deleted, user.is_email_verified = True
        │
        ├──── user clicks link after expiry window  ──► token deleted, error returned
        │
        ├──── user requests resend                  ──► old token deleted, new token created
        │
        └──── user re-registers (unverified email)  ──► old user + token deleted (CASCADE), new user + token created
```

---

## Validation Rules

| Rule | Where Enforced | Notes |
|------|---------------|-------|
| Token must exist in database | `selectors.email_verification_token_get_by_token` + verify service | Returns `None` if not found |
| Token must not be expired (`expires_at > now`) | `email_verification_verify` service | Expired records deleted on rejection |
| Duplicate email registration rejected if existing user is verified | `RegisterInputSerializer.validate_email` | Unverified duplicate → supersede in service |
| Duplicate email registration supersedes unverified user | `user_create` service (`@transaction.atomic`) | Old user deleted, new user created, new token issued |
| Resend returns same response regardless of email existence | `email_verification_resend` service + `ResendVerificationEmailView` | Prevents user enumeration |
