# Implementation Plan: Passkey Registration & Authentication

**Branch**: `004-passkey-auth` | **Date**: 2026-03-27 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-passkey-auth/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add WebAuthn-based passkey registration and authentication as an alternative to email/password. Users register with an email + passkey (discoverable credential), go through the existing email verification flow, and authenticate username-lessly via passkey assertion. Existing verified users can add passkeys to their accounts. Credential management (list, remove) and security safeguards (sign count validation, credential disabling on cloning detection, 5-passkey limit) are included. The `py_webauthn` library handles the WebAuthn ceremony logic.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Django 5.1.2, Django REST Framework, SimpleJWT, py_webauthn  
**Storage**: PostgreSQL (prod), SQLite (local/test) — new `WebAuthnCredential` model  
**Testing**: pytest with factory_boy  
**Target Platform**: Linux server (Docker) / macOS local dev  
**Project Type**: Web service (API-first, no frontend in scope)  
**Performance Goals**: Authentication in <10s end-to-end (server portion <200ms)  
**Constraints**: WebAuthn challenges expire after 5 minutes; max 5 passkeys per user  
**Scale/Scope**: Existing user base; adds 6 new API endpoints under `/api/auth/passkey/`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. HackSoftware Styleguide | PASS | Services for writes, selectors for reads, thin views, dedicated serializers |
| II. API-First Design | PASS | All passkey flows designed as REST endpoints first; RFC 9457 error envelope |
| III. Test-First Development | PASS | Tests will use factory_boy; each service gets happy + error path tests |
| IV. Code Quality | PASS | ruff, mypy strict on all new code |
| V. Structured Observability | PASS | structlog for all passkey events (registration, auth, cloning detection) |
| VI. Simplicity & Reuse | PASS | `py_webauthn` reuses well-maintained FIDO2 library; no speculative abstractions |
| VII. Poetry-Managed Toolchain | PASS | `poetry add py_webauthn`; all commands via `poetry run` |

**Pre-Phase 0 gate: PASS** — no violations.

## Project Structure

### Documentation (this feature)

```text
specs/004-passkey-auth/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── passkey.md       # Passkey API contract
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
users/
├── models.py            # + WebAuthnCredential model
├── managers.py          # unchanged
├── services.py          # + passkey registration, authentication, management services
├── selectors.py         # + passkey credential selectors
├── serializers.py       # + passkey input/output serializers
├── views.py             # + passkey API views
├── urls.py              # + passkey URL patterns under /api/auth/passkey/
├── conf.py              # + WEBAUTHN_* settings (RP ID, RP name, challenge timeout)
├── claims.py            # unchanged (JWT claims already generic)
├── permissions.py       # unchanged (uses IsAuthenticated)
├── admin.py             # + WebAuthnCredential admin registration
├── migrations/
│   └── 0003_add_webauthn_credential.py
└── tests/
    ├── factories.py     # + WebAuthnCredentialFactory
    └── test_passkey.py  # passkey service/view tests
```

**Structure Decision**: All passkey code lives in the existing `users` app since passkeys are an authentication method tightly coupled to the user model. No new Django app is needed — this follows simplicity (Principle VI) and the existing project layout.

## Complexity Tracking

> No constitution violations — table not required.
