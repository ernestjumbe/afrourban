# Quickstart: Passkey Registration & Authentication

**Feature**: 004-passkey-auth  
**Branch**: `004-passkey-auth`

## Prerequisites

- Python 3.11+
- Poetry installed
- Feature 003 (email verification) fully implemented
- Django development server running

## Setup

```bash
# Switch to feature branch
git checkout 004-passkey-auth

# Install new dependency
poetry add py_webauthn

# Run migrations (after creating them)
poetry run python manage.py makemigrations users
poetry run python manage.py migrate
```

## Configuration

Add to your Django settings (e.g., `afrourban/settings/local.py`):

```python
# WebAuthn / Passkey settings
USERS_WEBAUTHN_RP_ID = "localhost"
USERS_WEBAUTHN_RP_NAME = "Afrourban"
USERS_WEBAUTHN_ORIGIN = "http://localhost:8000"
USERS_WEBAUTHN_CHALLENGE_TIMEOUT_SECONDS = 300  # 5 minutes
USERS_WEBAUTHN_MAX_CREDENTIALS_PER_USER = 5
```

## New API Endpoints

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/api/auth/passkey/register/options/` | No | Get registration options |
| POST | `/api/auth/passkey/register/complete/` | No | Complete registration |
| POST | `/api/auth/passkey/authenticate/options/` | No | Get authentication options |
| POST | `/api/auth/passkey/authenticate/complete/` | No | Complete authentication |
| POST | `/api/auth/passkey/add/options/` | Yes | Get add-passkey options |
| POST | `/api/auth/passkey/add/complete/` | Yes | Complete passkey addition |
| GET | `/api/auth/passkey/` | Yes | List user's passkeys |
| DELETE | `/api/auth/passkey/{id}/` | Yes | Remove a passkey |

## New Files

| File | Purpose |
|------|---------|
| `users/models.py` | + `WebAuthnCredential` model |
| `users/services.py` | + Passkey registration, auth, management services |
| `users/selectors.py` | + Passkey credential selectors |
| `users/serializers.py` | + Passkey input/output serializers |
| `users/views.py` | + Passkey API views |
| `users/urls.py` | + Passkey URL patterns |
| `users/conf.py` | + WebAuthn app settings |
| `users/admin.py` | + WebAuthnCredential admin registration |
| `users/migrations/0003_add_webauthn_credential.py` | Migration |
| `users/tests/test_passkey.py` | Passkey tests |
| `users/tests/factories.py` | + `WebAuthnCredentialFactory` |

## Running Tests

```bash
# Run passkey-specific tests
poetry run pytest users/tests/test_passkey.py -v

# Run all tests
poetry run pytest -v
```

## Key Dependencies

- `py_webauthn` — WebAuthn ceremony handling (registration options, attestation verification, authentication options, assertion verification)
