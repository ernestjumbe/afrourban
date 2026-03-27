# Quickstart: Email Verification

**Branch**: `003-email-verification-registration`  
**Feature**: Add email verification step to user registration

---

## Prerequisites

- The project is already running locally (see root `README.md`)
- Poetry environment is active: `poetry shell` or prefix commands with `poetry run`

---

## Local Email Setup

For local development, configure Django to print emails to the console instead of sending them.

Add the following to `afrourban/settings/local.py`:

```python
# Email: log to console in local dev
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Override app-level email verification settings
USERS_EMAIL_VERIFICATION_BASE_URL = "http://localhost:3000"
USERS_EMAIL_VERIFICATION_SITE_NAME = "Afrourban (local)"
```

Sent emails will appear in the Django dev server terminal output. The `verification_url` printed in the email body will use `http://localhost:3000` as its base.

---

## Running Migrations

After the implementation is complete, apply the new migrations:

```bash
poetry run python manage.py migrate
```

The migration will:
1. Add `is_email_verified` (BooleanField, default `False`) to `CustomUser`
2. Run a data migration setting `is_email_verified = True` for all existing users
3. Create the `EmailVerificationToken` table

---

## Testing Email Verification Locally

### Step 1: Register a user

```bash
curl -s -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "StrongPass123!"}' | python -m json.tool
```

Expected response:
```json
{
  "email": "test@example.com"
}
```

### Step 2: Retrieve the token from console output

With `EMAIL_BACKEND = "...console.EmailBackend"`, the email body is written to the server terminal. Find a URL shaped like:

```
http://localhost:3000/registration/email-verification?token=<TOKEN>
```

Copy the token value.

### Step 3: Verify the email

```bash
curl -s -X POST http://localhost:8000/api/auth/email-verification/verify/ \
  -H "Content-Type: application/json" \
  -d '{"token": "<TOKEN>"}' | python -m json.tool
```

Expected response:
```json
{
  "status": "ok"
}
```

### Step 4: Confirm login now works

```bash
curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "StrongPass123!"}' | python -m json.tool
```

Expected response: JWT access and refresh tokens.

### Step 5: Test login block (before verifying)

Register a new user but do **not** verify. Attempt login:

```bash
curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "unverified@example.com", "password": "StrongPass123!"}' | python -m json.tool
```

Expected response (`401`):
```json
{
  "type": "about:blank",
  "title": "Unauthorized",
  "status": 401,
  "detail": "Email address has not been verified.",
  "code": "email_not_verified"
}
```

---

## Resend Verification Email

```bash
curl -s -X POST http://localhost:8000/api/auth/email-verification/resend/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}' | python -m json.tool
```

Expected response (always, regardless of whether the email exists):
```json
{
  "status": "ok"
}
```

---

## Configurable App Settings

All settings live in `users/conf.py` as a singleton `app_settings` object. They can be overridden from any Django settings file by adding the corresponding `USERS_*` key.

| Django settings key | Default | Description |
|---|---|---|
| `USERS_EMAIL_VERIFICATION_TOKEN_EXPIRY_DAYS` | `7` | Days before a token expires |
| `USERS_EMAIL_VERIFICATION_BASE_URL` | `""` | Base URL of the frontend app |
| `USERS_EMAIL_VERIFICATION_SITE_NAME` | `"Afrourban"` | Site name used in email subject/body |
| `USERS_EMAIL_VERIFICATION_FROM_EMAIL` | `settings.DEFAULT_FROM_EMAIL` | From address for verification emails |

Example override in `afrourban/settings/dev.py`:

```python
USERS_EMAIL_VERIFICATION_TOKEN_EXPIRY_DAYS = 1   # expire faster for testing
USERS_EMAIL_VERIFICATION_BASE_URL = "http://localhost:3000"
```

---

## Running the Tests

```bash
# Run all tests for the users app
poetry run pytest users/ -v

# Run only email verification tests
poetry run pytest users/ -v -k "email_verification"
```

---

## Docker / Compose

When running via Docker Compose, add the environment variables to the relevant `.env` file (e.g. `env/.env.local`):

```env
USERS_EMAIL_VERIFICATION_BASE_URL=http://localhost:3000
USERS_EMAIL_VERIFICATION_SITE_NAME=Afrourban (local)
```

And set the email backend in `afrourban/settings/local.py` as shown above.
