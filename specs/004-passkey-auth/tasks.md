# Tasks: Passkey Registration & Authentication

**Input**: Design documents from `/specs/004-passkey-auth/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/passkey.md, quickstart.md

**Tests**: Not explicitly requested — test tasks are omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependency, add WebAuthn app settings, create the WebAuthnCredential model, and register it in admin.

- [x] T001 Install py_webauthn dependency via `poetry add py_webauthn`
- [x] T002 Add WebAuthn settings properties (RP_ID, RP_NAME, ORIGIN, CHALLENGE_TIMEOUT_SECONDS, MAX_CREDENTIALS_PER_USER) to users/conf.py
- [x] T003 [P] Add USERS_WEBAUTHN_* settings to afrourban/settings/local.py for local development defaults

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core model, migration, factory, and admin — MUST be complete before ANY user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T004 Create WebAuthnCredential model (credential_id, public_key, sign_count, webauthn_user_id, device_label, is_enabled, created_at) with ForeignKey to CustomUser in users/models.py
- [x] T005 Generate migration 0003_add_webauthn_credential via `poetry run python manage.py makemigrations users`
- [x] T006 [P] Create WebAuthnCredentialFactory in users/tests/factories.py
- [x] T007 [P] Register WebAuthnCredential in Django admin with list_display, list_filter, search_fields, and readonly_fields in users/admin.py

**Checkpoint**: Foundation ready — WebAuthnCredential model exists, migrated, factory and admin available. User story implementation can now begin.

---

## Phase 3: User Story 1 — New User Registers with Passkey (Priority: P1) 🎯 MVP

**Goal**: A new visitor provides an email and creates a passkey credential. The account is created, email verification is triggered, and the user cannot authenticate until verified.

**Independent Test**: Initiate passkey registration with an email, complete the ceremony, confirm account creation, verify email via existing flow, and authenticate with the passkey.

### Implementation for User Story 1

- [x] T008 [US1] Implement challenge cache helpers (store_challenge, retrieve_and_delete_challenge) using Django cache with configurable TTL in users/services.py
- [x] T009 [US1] Implement passkey_register_options service: validate email not taken by verified account, supersede unverified account, generate registration options via py_webauthn generate_registration_options(), store challenge in cache, return options JSON and challenge_id in users/services.py
- [x] T010 [US1] Implement passkey_register_complete service: retrieve challenge from cache, verify registration response via py_webauthn verify_registration_response(), create user with password=None, create Profile, store WebAuthnCredential, trigger email verification, return user in users/services.py
- [x] T011 [P] [US1] Create PasskeyRegisterOptionsInputSerializer (email, display_name) and PasskeyRegisterOptionsOutputSerializer (challenge_id, options) in users/serializers.py
- [x] T012 [P] [US1] Create PasskeyRegisterCompleteInputSerializer (challenge_id, credential object) and PasskeyRegisterCompleteOutputSerializer (id, email, is_email_verified, message) in users/serializers.py
- [x] T013 [US1] Create PasskeyRegisterOptionsView (POST, AllowAny) calling passkey_register_options service in users/views.py
- [x] T014 [US1] Create PasskeyRegisterCompleteView (POST, AllowAny) calling passkey_register_complete service in users/views.py
- [x] T015 [US1] Add URL patterns for passkey/register/options/ and passkey/register/complete/ under auth_urlpatterns in users/urls.py

**Checkpoint**: User Story 1 complete — new users can register via passkey and receive a verification email. Authentication is blocked until email is verified.

---

## Phase 4: User Story 2 — Verified User Authenticates with Passkey (Priority: P1)

**Goal**: A user with a verified email authenticates via discoverable credential (no email entry). The system validates the passkey and returns JWT tokens.

**Independent Test**: Have a registered, email-verified user initiate passkey authentication, complete the assertion ceremony, and confirm JWT tokens are returned.

### Implementation for User Story 2

- [x] T016 [US2] Implement passkey_authenticate_options service: generate authentication options via py_webauthn generate_authentication_options() with empty allowCredentials, store challenge in cache, return options JSON and challenge_id in users/services.py
- [x] T017 [US2] Implement passkey_authenticate_complete service: retrieve challenge from cache, look up WebAuthnCredential by credential_id, verify assertion via py_webauthn verify_authentication_response(), validate sign count (disable credential on cloning detection), check is_email_verified, check is_enabled, issue JWT via CustomTokenObtainPairSerializer.get_token(), update sign_count, return tokens in users/services.py
- [x] T018 [P] [US2] Create PasskeyAuthenticateOptionsOutputSerializer (challenge_id, options) in users/serializers.py
- [x] T019 [P] [US2] Create PasskeyAuthenticateCompleteInputSerializer (challenge_id, credential object) and token output serializer in users/serializers.py
- [x] T020 [P] [US2] Implement passkey_credential_get_by_credential_id selector to look up enabled WebAuthnCredential by raw credential_id bytes in users/selectors.py
- [x] T021 [US2] Create PasskeyAuthenticateOptionsView (POST, AllowAny) calling passkey_authenticate_options service in users/views.py
- [x] T022 [US2] Create PasskeyAuthenticateCompleteView (POST, AllowAny) calling passkey_authenticate_complete service in users/views.py
- [x] T023 [US2] Add URL patterns for passkey/authenticate/options/ and passkey/authenticate/complete/ under auth_urlpatterns in users/urls.py

**Checkpoint**: User Stories 1 AND 2 complete — full passkey registration-to-authentication flow works end-to-end.

---

## Phase 5: User Story 3 — Existing User Adds a Passkey (Priority: P2)

**Goal**: An authenticated user with a verified email adds a passkey credential to their existing account.

**Independent Test**: Log in with email/password, initiate passkey addition, complete the ceremony, log out, and authenticate with the new passkey.

### Implementation for User Story 3

- [x] T024 [US3] Implement passkey_add_options service: check email verified, check max credentials limit (5), generate registration options with excludeCredentials listing user's existing credential IDs, store challenge in cache, return options JSON and challenge_id in users/services.py
- [x] T025 [US3] Implement passkey_add_complete service: retrieve challenge from cache, verify registration response, create WebAuthnCredential linked to authenticated user, return credential info in users/services.py
- [x] T026 [P] [US3] Create PasskeyAddOptionsInputSerializer (device_label) and PasskeyAddOptionsOutputSerializer (challenge_id, options) in users/serializers.py
- [x] T027 [P] [US3] Create PasskeyAddCompleteInputSerializer (challenge_id, credential) and PasskeyAddCompleteOutputSerializer (id, device_label, created_at, is_enabled) in users/serializers.py
- [x] T028 [US3] Create PasskeyAddOptionsView (POST, IsAuthenticated) calling passkey_add_options service in users/views.py
- [x] T029 [US3] Create PasskeyAddCompleteView (POST, IsAuthenticated) calling passkey_add_complete service in users/views.py
- [x] T030 [US3] Add URL patterns for passkey/add/options/ and passkey/add/complete/ under auth_urlpatterns in users/urls.py

**Checkpoint**: User Story 3 complete — existing verified users can add passkeys to their accounts.

---

## Phase 6: User Story 4 — User Manages Multiple Passkeys (Priority: P3)

**Goal**: A user can view a list of their registered passkeys and remove individual credentials, with safeguards for last-method removal.

**Independent Test**: Add multiple passkeys, list them, remove one, confirm the removed passkey no longer authenticates while others still do.

### Implementation for User Story 4

- [x] T031 [P] [US4] Implement passkey_credentials_list selector: return queryset of WebAuthnCredential for user ordered by created_at in users/selectors.py
- [x] T032 [P] [US4] Create PasskeyCredentialListOutputSerializer (id, device_label, created_at, is_enabled) in users/serializers.py
- [x] T033 [US4] Implement passkey_credential_remove service: verify credential belongs to user, prevent removal if last auth method (no password and only one passkey), delete credential in users/services.py
- [x] T034 [US4] Create PasskeyListView (GET, IsAuthenticated) calling passkey_credentials_list selector in users/views.py
- [x] T035 [US4] Create PasskeyRemoveView (DELETE, IsAuthenticated) calling passkey_credential_remove service in users/views.py
- [x] T036 [US4] Add URL patterns for passkey/ (GET list) and passkey/<int:credential_id>/ (DELETE) under auth_urlpatterns in users/urls.py

**Checkpoint**: All user stories complete — full passkey lifecycle (register, authenticate, add, list, remove) is functional.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Logging, edge case hardening, and validation run.

- [x] T037 [P] Add structlog events for all passkey operations (registration, authentication, cloning detection, credential disabled, credential removed) in users/services.py
- [x] T038 [P] Add WebAuthn local dev settings to afrourban/settings/test.py for test environment
- [x] T039 Run quickstart.md validation: install dependency, run migrations, verify all 8 endpoints respond correctly

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3–6)**: All depend on Foundational phase completion
  - US1 (Phase 3) and US2 (Phase 4) are both P1 but US2 depends on US1's registration flow for creating passkey users
  - US3 (Phase 5) is independent of US1/US2 (operates on existing password-based users)
  - US4 (Phase 6) depends on US3 or US1 (needs credentials to exist for list/remove)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — no dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) — shares challenge helpers from US1 (T008), so US1's T008-T010 should complete first
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) — reuses challenge helpers from US1, independent otherwise
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) — independent of other stories for implementation, but testing requires credentials created via US1 or US3

### Within Each User Story

- Services before views (views call services)
- Serializers can be built in parallel with services (different concerns)
- Views depend on both services and serializers
- URL patterns depend on views
- Core implementation before integration

### Parallel Opportunities

- T002 and T003 (settings files) can run in parallel
- T006 and T007 (factory and admin) can run in parallel after T004
- Within US1: T011 and T012 (serializers) can run in parallel with T008-T010 (services)
- Within US2: T018, T019, and T020 (serializers + selector) can run in parallel
- Within US3: T026 and T027 (serializers) can run in parallel
- Within US4: T031 and T032 (selector + serializer) can run in parallel
- T037 and T038 (logging + test settings) can run in parallel
- Once Foundational phase completes, US1 and US3 can start in parallel (independent flows)

---

## Parallel Example: User Story 1

```bash
# Launch serializers in parallel with services:
Task T011: "PasskeyRegisterOptionsInputSerializer in users/serializers.py"
Task T012: "PasskeyRegisterCompleteInputSerializer in users/serializers.py"
# (while simultaneously)
Task T008: "Challenge cache helpers in users/services.py"
Task T009: "passkey_register_options service in users/services.py"
Task T010: "passkey_register_complete service in users/services.py"

# Then views (depend on both services + serializers):
Task T013: "PasskeyRegisterOptionsView in users/views.py"
Task T014: "PasskeyRegisterCompleteView in users/views.py"

# Finally URL patterns:
Task T015: "URL patterns in users/urls.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)

1. Complete Phase 1: Setup (install py_webauthn, configure settings)
2. Complete Phase 2: Foundational (model, migration, factory, admin)
3. Complete Phase 3: User Story 1 — passkey registration
4. Complete Phase 4: User Story 2 — passkey authentication
5. **STOP and VALIDATE**: Full registration-to-authentication flow works
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test registration independently → Partial MVP
3. Add User Story 2 → Test authentication end-to-end → Deploy/Demo (MVP!)
4. Add User Story 3 → Test adding passkey to existing account → Deploy/Demo
5. Add User Story 4 → Test passkey management (list, remove) → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 → then User Story 2
   - Developer B: User Story 3 (independent path)
3. After US1+US2 and US3 merge: Developer A or B: User Story 4
4. Polish phase after all stories merge

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All WebAuthn binary fields use BinaryField; serialization uses Base64URL at API boundaries
- Challenge storage uses Django cache framework (not a model) — see research.md §3
- py_webauthn handles CBOR/COSE encoding internally — no manual parsing needed
