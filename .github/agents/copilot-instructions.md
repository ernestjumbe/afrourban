# afrourban Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-27

## Active Technologies
- PostgreSQL (via psycopg2-binary) (001-user-profile-apps)
- Python ^3.11 + Django 5.1.x, djangorestframework, djangorestframework-simplejwt (from feature 001) (002-age-verification-field)
- Python ^3.11 + Django 5.1.x, Django REST Framework, `rest_framework_simplejwt`, `structlog`, `factory_boy` (tests) (003-email-verification-registration)
- PostgreSQL (SQLite for local dev) — new `EmailVerificationToken` table; `is_email_verified` field on `CustomUser` (003-email-verification-registration)
- Python 3.11+ + Django 5.1.2, Django REST Framework, SimpleJWT, py_webauthn (004-passkey-auth)
- PostgreSQL (prod), SQLite (local/test) — new `WebAuthnCredential` model (004-passkey-auth)

- Python ^3.11 + Django 5.1.x, djangorestframework, djangorestframework-simplejwt, Pillow (profile images) (001-user-profile-apps)

## Project Structure

```text
backend/
frontend/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python ^3.11: Follow standard conventions

## Recent Changes
- 004-passkey-auth: Added Python 3.11+ + Django 5.1.2, Django REST Framework, SimpleJWT, py_webauthn
- 003-email-verification-registration: Added Python ^3.11 + Django 5.1.x, Django REST Framework, `rest_framework_simplejwt`, `structlog`, `factory_boy` (tests)
- 002-age-verification-field: Added Python ^3.11 + Django 5.1.x, djangorestframework, djangorestframework-simplejwt (from feature 001)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
