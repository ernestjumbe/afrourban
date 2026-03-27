# Tasks: Email Verification for User Registration

**Input**: Design documents from `/specs/003-email-verification-registration/`
**Branch**: `003-email-verification-registration`
**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/email-verification.md ✅

**Total tasks**: 27 | **User stories**: 4 | **MVP scope**: Phase 1 + Phase 2 + Phase 3 (US1)

---

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel with other tasks in the same phase that touch different files
- **[Story]**: User story this task belongs to (US1–US4)
- Exact file paths are included in every task description

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the app-level settings module that all other new code depends on.

- [X] T001 Create `users/conf.py` with `_AppSettings` class exposing `EMAIL_VERIFICATION_TOKEN_EXPIRY_DAYS` (default `7`), `EMAIL_VERIFICATION_BASE_URL` (default `""`), `EMAIL_VERIFICATION_FROM_EMAIL` (default `settings.DEFAULT_FROM_EMAIL`), and `EMAIL_VERIFICATION_SITE_NAME` (default `"Afrourban"`) via `getattr(django.conf.settings, "USERS_<KEY>", DEFAULT)` properties; export a module-level `app_settings` singleton

**Checkpoint**: `users/conf.py` importable; defaults are accessible as `app_settings.EMAIL_VERIFICATION_TOKEN_EXPIRY_DAYS`, etc.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database model changes, migration, and shared test fixtures that ALL user stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Add `is_email_verified = models.BooleanField(default=False)` to `CustomUser` in `users/models.py`; add `EmailVerificationToken` model with `user (OneToOneField → CustomUser, CASCADE, related_name="email_verification_token")`, `token (CharField(max_length=64), unique=True, db_index=True)`, `created_at (DateTimeField, auto_now_add=True)`, `expires_at (DateTimeField)` to `users/models.py`
- [X] T003 Create `users/migrations/0002_add_email_verification.py`: (1) add `is_email_verified` field, (2) `RunPython` data migration sets `is_email_verified=True` for all existing users, (3) create `EmailVerificationToken` table
- [X] T004 [P] Update `RegisterInputSerializer.validate_email()` in `users/serializers.py` to scope the duplicate-email check to `User.objects.filter(email__iexact=email, is_email_verified=True)` so registration against an unverified address is not rejected at the serializer layer
- [X] T005 [P] Add `EmailVerificationTokenFactory` to `users/tests/factories.py` with `user (SubFactory(UserFactory))`, `token (LazyFunction(lambda: secrets.token_urlsafe(32)))`, `expires_at (LazyFunction(lambda: now() + timedelta(days=7)))`

**Checkpoint**: `python manage.py migrate` succeeds; `CustomUser` has `is_email_verified`; `EmailVerificationToken` table exists; `RegisterInputSerializer` passes unverified-email addresses; factory is importable.

---

## Phase 3: User Story 1 — New User Verifies Email After Registration (Priority: P1) 🎯 MVP

**Goal**: Register a new user → receive verification email → submit token → email marked verified → login succeeds.

**Independent Test**: Register a fresh user via `POST /api/auth/register/`, read the token from console email output, `POST /api/auth/email-verification/verify/` with the token, confirm `200 {"status": "ok"}`, confirm the user's `is_email_verified` is `True`, confirm `POST /api/auth/token/` now succeeds.

- [X] T006 [P] [US1] Create `users/templates/users/emails/email_verification.html` rendering a styled HTML email with greeting, explanation paragraph, prominent verification link (`{{ verification_url }}`), expiry notice (`{{ expiry_days }} days`), and footer with `{{ site_name }}`
- [X] T007 [P] [US1] Create `users/templates/users/emails/email_verification.txt` as the plain-text counterpart, with the same context variables as the HTML template (`{{ verification_url }}`, `{{ expiry_days }}`, `{{ site_name }}`, `{{ user.email }}`)
- [X] T008 [P] [US1] Add `email_verification_token_get_by_token(token: str) -> EmailVerificationToken | None` selector to `users/selectors.py` using `EmailVerificationToken.objects.select_related("user").filter(token=token).first()`
- [X] T009 [US1] Add `email_verification_token_create(user: CustomUser) -> EmailVerificationToken` service to `users/services.py` that generates a token via `secrets.token_urlsafe(32)`, sets `expires_at = now() + timedelta(days=app_settings.EMAIL_VERIFICATION_TOKEN_EXPIRY_DAYS)`, and saves the record
- [X] T010 [US1] Add `email_verification_send(user: CustomUser, token_obj: EmailVerificationToken) -> None` service to `users/services.py` that builds `verification_url = f"{app_settings.EMAIL_VERIFICATION_BASE_URL}/registration/email-verification?token={token_obj.token}"`, renders both templates via `render_to_string`, and calls `send_mail(subject, text_body, from_email, [user.email], html_message=html_body)`
- [X] T011 [US1] Update `user_create()` service in `users/services.py` to: (a) within the existing `@transaction.atomic` block, detect a pre-existing unverified account (`User.objects.filter(email__iexact=email, is_email_verified=False)`) and delete it (CASCADE removes any existing token); (b) after creating the new `User` and `Profile`, call `email_verification_token_create()` then `email_verification_send()`
- [X] T012 [P] [US1] Add `VerifyEmailInputSerializer(serializers.Serializer)` with `token = serializers.CharField()` field to `users/serializers.py`
- [X] T013 [US1] Add `email_verification_verify(token: str) -> None` service to `users/services.py` that: (1) calls `email_verification_token_get_by_token(token)`; (2) if not found, raises `ValidationError` with `code="token_invalid"`; (3) if `now() >= token_obj.expires_at`, deletes token and raises `ValidationError` with `code="token_expired"`; (4) otherwise, sets `token_obj.user.is_email_verified = True`, saves, and deletes the token
- [X] T014 [US1] Add `VerifyEmailView(APIView)` to `users/views.py` with `permission_classes = [AllowAny]`, `post()` deserialising with `VerifyEmailInputSerializer`, calling `email_verification_verify(token)`, returning `Response({"status": "ok"})`
- [X] T015 [US1] Register `path("email-verification/verify/", VerifyEmailView.as_view(), name="email_verification_verify")` in `users/urls.py`
- [X] T016 [P] [US1] Write US1 tests in `users/tests/test_email_verification.py`: `test_register_sends_verification_email`, `test_verify_valid_token_returns_200`, `test_verify_marks_email_verified`, `test_verified_user_can_login`, `test_register_supersedes_existing_unverified_account`

**Checkpoint**: `POST /api/auth/register/` sends an email; `POST /api/auth/email-verification/verify/` with a valid token returns `200 {"status": "ok"}`; `CustomUser.is_email_verified` is set to `True`; login succeeds after verification; re-registering an unverified email replaces the old account.

---

## Phase 4: User Story 2 — Unverified User Is Blocked from Login (Priority: P1)

**Goal**: Any user with `is_email_verified=False` cannot obtain JWT tokens; the error response is distinguishable from wrong-credentials errors.

**Independent Test**: Create a user via factory with `is_email_verified=False`, attempt `POST /api/auth/token/`, confirm `401` response with `"code": "email_not_verified"`.

- [X] T017 [US2] In `CustomTokenObtainPairSerializer.validate()` in `users/serializers.py`, after credentials are validated, check `user.is_email_verified`; if `False`, raise `AuthenticationFailed(detail="Email address has not been verified.", code="email_not_verified")`
- [X] T018 [P] [US2] Write US2 tests in `users/tests/test_email_verification.py`: `test_unverified_user_login_blocked_returns_401`, `test_unverified_user_error_code_is_email_not_verified`, `test_verified_user_login_succeeds`, `test_expired_token_user_login_still_blocked`

**Checkpoint**: `POST /api/auth/token/` for an unverified user returns `401` with `code: email_not_verified`; verified users are unaffected.

---

## Phase 5: User Story 3 — Expired or Invalid Token Is Rejected (Priority: P2)

**Goal**: The verification endpoint correctly differentiates expired tokens (deleting them) from never-issued or already-consumed tokens, and returns appropriate error codes in each case.

**Independent Test**: Create an `EmailVerificationToken` via factory with `expires_at` in the past; submit to verify endpoint; confirm `400` with `code: token_expired` and confirm the token record was deleted. Submit a random string; confirm `400` with `code: token_invalid`.

- [X] T019 [US3] Verify `email_verification_verify()` in `users/services.py` fully handles all error branches: (1) token record missing → `token_invalid`; (2) token exists but `now() >= expires_at` → delete record and raise `token_expired`; (3) happy path → delete record and set `is_email_verified=True` (this service was scaffolded in T013; confirm expiry deletion and error codes are correct)
- [X] T020 [P] [US3] Write US3 tests in `users/tests/test_email_verification.py`: `test_expired_token_returns_400_token_expired`, `test_expired_token_is_deleted_from_db`, `test_invalid_token_string_returns_400_token_invalid`, `test_already_consumed_token_returns_400_token_invalid`

**Checkpoint**: Expired token → `400 token_expired` + record deleted; unknown token → `400 token_invalid`; consumed token (already deleted) → `400 token_invalid`.

---

## Phase 6: User Story 4 — User Requests a New Verification Email (Priority: P2)

**Goal**: Users can trigger a fresh verification email via an unauthenticated endpoint; the endpoint is enumeration-safe (always `200 OK`).

**Independent Test**: Register and do not verify; call `POST /api/auth/email-verification/resend/` with the email; confirm a new email is sent with a fresh token; verify using the new token; confirm `200` and login now works. Call resend with a verified email or unknown email; confirm `200` in all cases.

- [X] T021 [P] [US4] Add `ResendVerificationEmailInputSerializer(serializers.Serializer)` with `email = serializers.EmailField()` to `users/serializers.py`
- [X] T022 [US4] Add `email_verification_resend(email: str) -> None` service to `users/services.py` that: (1) looks up user by email; (2) if not found or `is_email_verified=True`, returns silently; (3) otherwise deletes any existing `EmailVerificationToken` for the user, calls `email_verification_token_create()` then `email_verification_send()`; always returns without raising
- [X] T023 [US4] Add `ResendVerificationEmailView(APIView)` to `users/views.py` with `permission_classes = [AllowAny]`, `post()` deserialising with `ResendVerificationEmailInputSerializer`, calling `email_verification_resend(email)`, returning `Response({"status": "ok"})`
- [X] T024 [US4] Register `path("email-verification/resend/", ResendVerificationEmailView.as_view(), name="email_verification_resend")` in `users/urls.py`
- [X] T025 [P] [US4] Write US4 tests in `users/tests/test_email_verification.py`: `test_resend_for_unverified_user_sends_email`, `test_resend_creates_new_token`, `test_resend_deletes_old_token`, `test_resend_for_verified_user_returns_200_no_email_sent`, `test_resend_for_unknown_email_returns_200_no_email_sent`

**Checkpoint**: `POST /api/auth/email-verification/resend/` returns `200` in all cases; unverified user receives a new email with a valid fresh token; old token is replaced.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Observability, type safety, and code quality pass across all new code.

- [X] T026 [P] Add `structlog.get_logger()` log events to all new/modified service functions in `users/services.py`: `email_verified` (on success in verify), `email_verification_token_expired` (on expiry rejection), `email_verification_resend_sent` (on resend), `email_verification_blocked_login` (on login block — add to serializer), `email_verification_superseded` (on unverified account replacement in user_create)
- [X] T027 [P] Run `poetry run mypy users/` and resolve all type annotation errors in new functions across `users/conf.py`, `users/models.py`, `users/services.py`, `users/selectors.py`, `users/serializers.py`, `users/views.py`
- [X] T028 [P] Run `poetry run ruff check . --fix` and resolve any remaining linting or import-order warnings across all modified files

---

## Dependencies

```
Phase 1 (T001)
    └─► Phase 2 (T002 → T003; T004 [P], T005 [P])
            └─► Phase 3 US1 (T006–T016)
                    └─► Phase 4 US2 (T017–T018)
                            └─► Phase 5 US3 (T019–T020)
                                    └─► Phase 6 US4 (T021–T025)
                                                └─► Final Phase (T026–T028)
```

**Story independence notes**:
- US2 only requires the Foundational `is_email_verified` field and `CustomTokenObtainPairSerializer` change — it does not depend on US1's verify endpoint. Sequenced after US1 to avoid serializer file conflicts.
- US3 refines the service implemented in US1 (T013) — add it as a follow-up rather than extending T013 significantly.
- US4 requires email templates (T006, T007) and `email_verification_token_create` (T009); these are delivered in Phase 3.

---

## Parallel Execution Examples

### Within Phase 2 — after T002 and T003 complete:
```
T004 (serializers.py)   ─┐
T005 (factories.py)     ─┘  run in parallel
```

### Within Phase 3 — can start once Phase 2 is complete:
```
T006 (html template)    ─┐
T007 (txt template)     ─┤
T008 (selectors.py)     ─┤  run in parallel
T012 (serializers.py)   ─┘

then: T009 → T010 → T011 (all in services.py, sequential)
then: T013 → T014 → T015 (views.py → urls.py → sequential; T016 tests can [P])
```

### Within Final Phase — all tasks are [P]:
```
T026 (structlog)   ─┐
T027 (mypy)        ─┤  all in parallel
T028 (ruff)        ─┘
```

---

## Implementation Strategy

**MVP (deliver first)**: Phase 1 + Phase 2 + Phase 3 (US1).  
This delivers the complete happy path: registration sends email → user verifies → login works.

**Increment 2**: Phase 4 (US2) — enforce the login gate.  
**Increment 3**: Phase 5 (US3) — harden token expiry/invalid error paths.  
**Increment 4**: Phase 6 (US4) — add resend capability.  
**Increment 5**: Final Phase — observability and quality pass.

Each increment is independently deployable and testable.
