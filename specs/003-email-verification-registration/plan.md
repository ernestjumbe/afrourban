# Implementation Plan: Email Verification for User Registration

**Branch**: `003-email-verification-registration` | **Date**: 2026-03-27 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-email-verification-registration/spec.md`

## Summary

Add an email verification step to the user registration flow: on registration a one-time opaque token is persisted, a verification email (HTML + text templates) is dispatched via `send_mail`, and a REST endpoint validates the token and marks the user's email as verified. Users who have not verified their email are blocked from logging in. A second unauthenticated endpoint allows resending the verification email by email address.

## Technical Context

**Language/Version**: Python ^3.11  
**Primary Dependencies**: Django 5.1.x, Django REST Framework, `rest_framework_simplejwt`, `structlog`, `factory_boy` (tests)  
**Storage**: PostgreSQL (SQLite for local dev) — new `EmailVerificationToken` table; `is_email_verified` field on `CustomUser`  
**Testing**: pytest via `poetry run pytest`; factories via `factory_boy`  
**Target Platform**: Linux server (Docker/Gunicorn)  
**Project Type**: Django REST API (web service)  
**Performance Goals**: No additional constraints beyond existing API requirements  
**Constraints**: RFC 9457 Problem Details error envelope; mypy strict; zero Ruff warnings  
**Scale/Scope**: Affects all new user registrations; existing users will be grandfathered as verified (migration default)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. HackSoftware Styleguide | ✅ PASS | Token logic in `services.py`; lookup in `selectors.py`; views call services only |
| II. API-First Design | ✅ PASS | Two new REST endpoints designed before any template or UI work |
| III. Test-First Development | ✅ PASS | Tests specified in research.md; factory additions defined |
| IV. Code Quality | ✅ PASS | Type annotations on all new functions; mypy strict; Ruff enforced |
| V. Structured Observability | ✅ PASS | structlog log events defined at all key operations |
| VI. Simplicity & Reuse | ✅ PASS | Django `send_mail` + `render_to_string` used; `secrets.token_urlsafe` for token generation; no new dependencies |
| VII. Poetry-Managed Toolchain | ✅ PASS | All commands via `poetry run` |

**No violations. Phase 0 research may proceed.**

## Project Structure

### Documentation (this feature)

```text
specs/003-email-verification-registration/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── email-verification.md   # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks — NOT created here)
```

### Source Code Changes (repository root)

```text
users/
├── models.py                   # MODIFY: add is_email_verified + EmailVerificationToken
├── managers.py                 # NO CHANGE
├── services.py                 # MODIFY: user_create sends verification email;
│                               #         add email_verification_token_create,
│                               #         email_verification_verify,
│                               #         email_verification_resend
├── selectors.py                # MODIFY: add email_verification_token_get_by_token
├── serializers.py              # MODIFY: validate_email only rejects verified duplicates;
│                               #         add VerifyEmailInputSerializer,
│                               #         ResendVerificationEmailInputSerializer
├── views.py                    # MODIFY: add VerifyEmailView, ResendVerificationEmailView
├── urls.py                     # MODIFY: register two new endpoints
├── conf.py                     # NEW: app-level settings with defaults
├── migrations/
│   └── 0002_add_email_verification.py   # NEW
├── templates/
│   └── users/
│       └── emails/
│           ├── email_verification.html  # NEW
│           └── email_verification.txt   # NEW
└── tests/
    ├── factories.py            # MODIFY: add EmailVerificationTokenFactory
    └── test_email_verification.py  # NEW: full test suite
```

**Structure Decision**: Single Django app (Option 1). All changes are within the existing `users` app. No new top-level directories. Templates use Django app-directories convention (`APP_DIRS: True` already set in `base.py`).

## Complexity Tracking

> No constitution violations. Section intentionally empty.


| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

---

## Phase 0: Research Summary

*Full findings in [research.md](research.md)*

### Key Decisions

| Decision | Chosen | Alternatives Considered |
|----------|--------|------------------------|
| Token generation | `secrets.token_urlsafe(32)` — 256-bit entropy, URL-safe, std library | `uuid.uuid4()` (weaker entropy, not URL-safe); external library (unnecessary dependency) |
| Token storage | `EmailVerificationToken` model, `OneToOneField(CustomUser)` | Store as field on User (couples model to verification flow); Redis/cache (persistence risk) |
| Token URL placement | Query parameter `?token=<value>` | Path segment (spec FR-011 explicitly chose query param) |
| App settings | `users/conf.py` singleton using `getattr(django.conf.settings, KEY, DEFAULT)` | `django-environ` (overhead); hardcoded defaults (not user-overridable) |
| Email dispatch | `render_to_string` + `send_mail(html_message=...)` | External email SDK (not required; `send_mail` satisfies requirements) |
| Login gate | Override `CustomTokenObtainPairSerializer.validate()`, raise `AuthenticationFailed` with `code: email_not_verified` | Middleware (too broad); permission class (wrong layer for auth) |
| Re-registration (unverified) | Delete existing unverified `User` + `EmailVerificationToken` in `@transaction.atomic` service, create new user | Update existing user (identity confusion); reject duplicate (breaks spec FR-012) |
| Expired token cleanup | Delete token at point of rejection (lazy deletion) | Celery periodic task (over-engineering; no Celery in current stack); database trigger (not portable) |
| Existing user migration | Data migration sets `is_email_verified = True` for all existing users | Default `False` (would break all existing user logins) |

### Resolved Clarifications

All five clarification questions from `/speckit.clarify` are resolved:

1. **Token storage** → Opaque token stored in `EmailVerificationToken` DB table (not JWT, not cache)
2. **Resend auth** → Unauthenticated by email address; enumeration-safe (always `200 OK`)
3. **Re-registration with unverified email** → Supersede: delete old unverified account, create new
4. **Token URL format** → Query parameter: `?token=<value>`
5. **Expired token cleanup** → Delete at point of rejection (no cleanup job needed)

---

## Phase 1: Design Summary

*Full details in [data-model.md](data-model.md), [contracts/email-verification.md](contracts/email-verification.md), [quickstart.md](quickstart.md)*

### Data Model Changes

1. **`CustomUser`** — Add `is_email_verified = BooleanField(default=False)`. Data migration sets all existing users to `True`.
2. **`EmailVerificationToken`** — New model with `user (OneToOneField)`, `token (CharField, unique)`, `created_at`, `expires_at`. No `is_consumed` flag — token is deleted on use.

### Interface Contracts

Two new unauthenticated endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/email-verification/verify/` | `POST` | Verify token, mark email verified |
| `/api/auth/email-verification/resend/` | `POST` | Resend verification email by email address |

One modified existing endpoint:

| Endpoint | Change |
|----------|--------|
| `POST /api/auth/token/` | Adds `401 email_not_verified` error for unverified users |

### Post-Design Constitution Check

All 7 principles re-evaluated after design. No new violations introduced:

- **I (HackSoftware)**: Service layer holds all verification logic; views remain thin ✅
- **II (API-First)**: Both endpoints designed before any implementation ✅
- **III (Test-First)**: `test_email_verification.py` test file specified with full scenario coverage ✅
- **IV (Code Quality)**: No new dependencies; type annotations on all new functions planned ✅
- **V (Observability)**: structlog events defined for verification, resend, and login gate ✅
- **VI (Simplicity)**: Lazy cleanup; single app; no new infrastructure ✅
- **VII (Poetry)**: All toolchain commands use `poetry run` ✅

---

## Next Step

Run `/speckit.tasks` to generate the task breakdown in `tasks.md`.
