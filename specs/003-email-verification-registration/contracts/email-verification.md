# API Contract: Email Verification

**Branch**: `003-email-verification-registration`  
**App**: `users`  
**Base path**: `/api/auth/`  
**Error format**: RFC 9457 Problem Details (all error responses)  
**Authentication**: All endpoints in this contract are unauthenticated (`AllowAny`)

---

## Endpoint 1: Verify Email

**`POST /api/auth/email-verification/verify/`**

Validates a verification token. If the token is valid and non-expired, marks the associated user's email as verified and deletes the token record. If the token is expired, the record is deleted and an error is returned.

### Request

**Headers**

| Header | Value | Required |
|--------|-------|----------|
| `Content-Type` | `application/json` | Yes |

**Body**

```json
{
  "token": "string"
}
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `token` | string | Yes | Non-empty |

### Responses

**`200 OK` — Token valid, email verified**

```json
{
  "status": "ok"
}
```

**`400 Bad Request` — Token expired**

```json
{
  "type": "about:blank",
  "title": "Bad Request",
  "status": 400,
  "detail": "Verification token has expired.",
  "instance": "/api/auth/email-verification/verify/",
  "code": "token_expired"
}
```

**`400 Bad Request` — Token invalid or not found**

```json
{
  "type": "about:blank",
  "title": "Bad Request",
  "status": 400,
  "detail": "Verification token is invalid.",
  "instance": "/api/auth/email-verification/verify/",
  "code": "token_invalid"
}
```

**`400 Bad Request` — Request body invalid**

```json
{
  "type": "about:blank",
  "title": "Bad Request",
  "status": 400,
  "detail": "Validation failed",
  "instance": "/api/auth/email-verification/verify/",
  "errors": {
    "token": ["This field is required."]
  }
}
```

### Behaviour Notes

- A token that has already been verified (i.e. deleted from the database) returns the same `token_invalid` response as a never-issued token. No distinction is made.
- Expiry check: `expires_at <= now()` → expired.
- On expiry: token record deleted, `token_expired` error returned.
- On success: token record deleted, `user.is_email_verified` set to `True`.

---

## Endpoint 2: Resend Verification Email

**`POST /api/auth/email-verification/resend/`**

Requests a new verification email for an unverified account. To prevent user enumeration, the response is always `200 OK` regardless of whether the supplied email address exists, is already verified, or belongs to an unverified account.

### Request

**Headers**

| Header | Value | Required |
|--------|-------|----------|
| `Content-Type` | `application/json` | Yes |

**Body**

```json
{
  "email": "string"
}
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `email` | string | Yes | Valid email format |

### Responses

**`200 OK` — Always returned (enumeration-safe)**

```json
{
  "status": "ok"
}
```

**`400 Bad Request` — Request body invalid**

```json
{
  "type": "about:blank",
  "title": "Bad Request",
  "status": 400,
  "detail": "Validation failed",
  "instance": "/api/auth/email-verification/resend/",
  "errors": {
    "email": ["Enter a valid email address."]
  }
}
```

### Behaviour Notes

- If the email address belongs to an unverified user: any existing token for that user is deleted, a new token is created, and a new verification email is sent.
- If the email address belongs to a verified user: no action is taken; `200 OK` returned.
- If the email address does not exist: no action is taken; `200 OK` returned.
- The service logs attempted resends for monitoring purposes (`structlog`), but the log is not exposed to the caller.

---

## Modified Endpoint: Token Obtain (Login)

**`POST /api/auth/token/`** — behaviour change only (no contract change)

The existing `CustomTokenObtainPairSerializer` is modified to reject users whose `is_email_verified` is `False`.

**New error response — `401 Unauthorized` — Email not verified**

```json
{
  "type": "about:blank",
  "title": "Unauthorized",
  "status": 401,
  "detail": "Email address has not been verified.",
  "instance": "/api/auth/token/",
  "code": "email_not_verified"
}
```

This error is distinct from the existing incorrect-credentials `401` (which uses `detail: "No active account found with the given credentials"`). Frontend clients MUST differentiate on the `code` field.

---

## URL Registration

New paths added to `users/urls.py` under the existing `auth_urlpatterns`:

```python
path("email-verification/verify/",  VerifyEmailView.as_view(),  name="email_verification_verify"),
path("email-verification/resend/",  ResendVerificationEmailView.as_view(), name="email_verification_resend"),
```

Mounted at `/api/auth/` → full paths:
- `POST /api/auth/email-verification/verify/`
- `POST /api/auth/email-verification/resend/`

---

## Email Template Contract

The verification email is sent with both a plain text and HTML version. The following template context variables are passed to both templates.

| Variable | Type | Source | Example |
|----------|------|--------|---------|
| `user` | `CustomUser` | The recipient user object | — |
| `verification_url` | `str` | `{base_url}/registration/email-verification?token={token}` | `https://app.afrourban.com/registration/email-verification?token=abc123` |
| `base_url` | `str` | `app_settings.EMAIL_VERIFICATION_BASE_URL` | `https://app.afrourban.com` |
| `expiry_days` | `int` | `app_settings.EMAIL_VERIFICATION_TOKEN_EXPIRY_DAYS` | `7` |
| `site_name` | `str` | `app_settings.EMAIL_VERIFICATION_SITE_NAME` | `Afrourban` |

**Template paths** (resolved via `APP_DIRS: True`):
- `users/templates/users/emails/email_verification.html`
- `users/templates/users/emails/email_verification.txt`

**Subject line**: `"Verify your email address – {site_name}"`
