---

description: "Task list for username registration and email privacy"
---

# Tasks: Username Registration and Email Privacy

**Input**: Design documents from `/specs/006-add-username-privacy/`  
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED by the constitution and by this feature's success criteria; include unit/integration/contract coverage per user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no unmet dependencies)
- **[Story]**: Which user story this task belongs to (`US1`, `US2`, `US3`, `US4`)
- Every task includes concrete file path(s)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare test scaffolding and shared documentation touchpoints.

- [X] T001 Create feature test modules `users/tests/test_registration.py`, `users/tests/test_username_change.py`, `users/tests/test_api_email_visibility.py`, `users/tests/test_migrations_username_backfill.py`, and `profiles/tests/test_api_email_visibility.py`
- [X] T002 [P] Extend test data builders for username/ownership scenarios in `users/tests/factories.py` and `profiles/tests/factories.py`
- [X] T003 [P] Add feature placeholders for username/cooldown behavior in `docs/api/endpoints.md` and `docs/api/README.md`
- [X] T004 [P] Add settings override placeholders for cooldown testing in `afrourban/settings/base.py` and `afrourban/settings/test.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish core schema/configuration/validation foundations used by all stories.

**⚠️ CRITICAL**: No user story implementation starts before this phase is complete.

- [X] T005 Add `username` and `username_changed_at` fields plus model-level constraints metadata in `users/models.py`
- [X] T006 Add username cooldown accessor (`USERS_USERNAME_CHANGE_COOLDOWN_DAYS`) in `users/conf.py`
- [X] T007 Create schema migration for username fields/indexes in `users/migrations/0004_add_username_fields.py`
- [X] T008 [P] Implement shared username normalization and format-validation helpers in `users/services.py`
- [X] T009 [P] Implement shared ownership/role email-visibility helper utilities in `users/serializers.py`
- [X] T010 Add structured logging hooks for username/cooldown/privacy outcomes in `users/services.py` and `users/views.py`
- [X] T011 Confirm API route grouping remains compatible with new auth endpoint under `/api/v1/` in `users/urls.py` and `afrourban/urls.py`

**Checkpoint**: Foundation complete; user story phases can begin.

---

## Phase 3: User Story 1 - Register with Username, Login with Email (Priority: P1) 🎯 MVP

**Goal**: Require username at registration while preserving email/password authentication behavior.

**Independent Test**: Register with valid username succeeds; missing/invalid username fails; token login still succeeds with email/password.

### Tests for User Story 1 (required) ⚠️

- [X] T012 [P] [US1] Add registration tests for missing/invalid username validation in `users/tests/test_registration.py`
- [X] T013 [P] [US1] Add registration tests for case-insensitive username uniqueness collisions in `users/tests/test_registration.py`
- [X] T014 [US1] Add authentication regression test proving email/password login remains canonical in `users/tests/test_registration.py`

### Implementation for User Story 1

- [X] T015 [US1] Require and validate `username` in registration serializer contract in `users/serializers.py`
- [X] T016 [US1] Persist registration username in user creation flow in `users/services.py`
- [X] T017 [US1] Wire registration view to pass validated username into service layer in `users/views.py`
- [X] T018 [US1] Update registration API contract documentation with required username semantics in `docs/api/endpoints.md` and `specs/006-add-username-privacy/contracts/username-and-email-privacy.md`

**Checkpoint**: User Story 1 is independently functional and ready for MVP validation.

---

## Phase 4: User Story 2 - Preserve Existing Accounts During Username Rollout (Priority: P2)

**Goal**: Backfill usernames only for missing/blank legacy users and preserve existing non-empty usernames.

**Independent Test**: Migration fills missing/blank usernames from email and leaves existing non-empty usernames unchanged.

### Tests for User Story 2 (required) ⚠️

- [X] T019 [P] [US2] Add migration tests for backfilling missing/blank usernames from email in `users/tests/test_migrations_username_backfill.py`
- [X] T020 [US2] Add migration tests confirming existing non-empty usernames are preserved in `users/tests/test_migrations_username_backfill.py`

### Implementation for User Story 2

- [X] T021 [US2] Implement data migration for missing/blank username backfill in `users/migrations/0005_backfill_missing_usernames.py`
- [X] T022 [US2] Implement migration-safe normalization/collision handling for backfill writes in `users/migrations/0005_backfill_missing_usernames.py`
- [X] T023 [US2] Enforce post-backfill username integrity constraints in `users/migrations/0006_enforce_username_integrity.py` and `users/models.py`
- [X] T024 [US2] Document rollout/backfill expectations and operator checks in `specs/006-add-username-privacy/quickstart.md`

**Checkpoint**: User Story 2 is independently verifiable with migration-only test coverage.

---

## Phase 5: User Story 3 - Protect Non-Owned User Emails (Priority: P3)

**Goal**: Ensure non-privileged users never receive non-owned emails, while authorized admin/staff operations retain allowed access.

**Independent Test**: Non-privileged non-owned user objects omit email; owned objects keep allowed email; authorized admin/staff non-owned responses preserve email.

### Tests for User Story 3 (required) ⚠️

- [X] T025 [P] [US3] Add API tests for non-privileged non-owned email redaction in `users/tests/test_api_email_visibility.py`
- [X] T026 [P] [US3] Add API tests for owned-object email visibility in `users/tests/test_api_email_visibility.py`
- [X] T027 [P] [US3] Add profile endpoint tests for ownership-aware email behavior in `profiles/tests/test_api_email_visibility.py`

### Implementation for User Story 3

- [X] T028 [US3] Apply ownership-aware email projection in user serializers for non-privileged contexts in `users/serializers.py`
- [X] T029 [US3] Apply/verify redaction behavior on profile-facing public payload serializers in `profiles/serializers.py` and `profiles/views.py`
- [X] T030 [US3] Preserve explicit admin/staff visibility behavior for authorized operations in `users/serializers.py` and `users/views.py`
- [X] T031 [US3] Update published visibility matrix and examples in `docs/api/endpoints.md` and `specs/006-add-username-privacy/contracts/username-and-email-privacy.md`

**Checkpoint**: User Story 3 is independently testable via API visibility scenarios.

---

## Phase 6: User Story 4 - Change Username with Cooldown (Priority: P4)

**Goal**: Provide authenticated username change with full validation, case-insensitive uniqueness, and configurable cooldown (default 7 days, no initial-creation cooldown).

**Independent Test**: First change succeeds, repeated change before cooldown fails, post-cooldown change succeeds, invalid/duplicate usernames fail, configurable cooldown is honored.

### Tests for User Story 4 (required) ⚠️

- [X] T032 [P] [US4] Add API tests for first-change success and cooldown-active rejection in `users/tests/test_username_change.py`
- [X] T033 [P] [US4] Add API tests for cooldown expiry and configurable cooldown days in `users/tests/test_username_change.py`
- [X] T034 [P] [US4] Add API tests for invalid-format and duplicate username changes in `users/tests/test_username_change.py`

### Implementation for User Story 4

- [X] T035 [US4] Add username-change request/response serializers in `users/serializers.py`
- [X] T036 [US4] Implement username-change service logic with cooldown and uniqueness enforcement in `users/services.py`
- [X] T037 [US4] Add authenticated username-change API view orchestration in `users/views.py`
- [X] T038 [US4] Register `PATCH /api/v1/auth/username/` endpoint in `users/urls.py`
- [X] T039 [US4] Implement cooldown configuration wiring and defaults in `users/conf.py` and `afrourban/settings/base.py`
- [X] T040 [US4] Emit structured logs for username-change outcomes (`success`, `cooldown_active`, `username_taken`, `invalid_format`) in `users/services.py`
- [X] T041 [US4] Update endpoint contract/docs for username change and cooldown semantics in `docs/api/endpoints.md` and `specs/006-add-username-privacy/contracts/username-and-email-privacy.md`

**Checkpoint**: User Story 4 is independently testable through the username-change endpoint.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final documentation/schema publication and full quality validation across all stories.

- [X] T042 [P] Regenerate schema artifacts for publication in `docs/api/openapi-public.yaml` and `docs/api/openapi-internal.yaml`
- [X] T043 [P] Refresh docs runbook and endpoint catalog in `docs/api/README.md` and `docs/api/endpoints.md`
- [X] T044 Run full quality gates and capture outcomes in `specs/006-add-username-privacy/quickstart.md`
- [X] T045 [P] Add explicit compatibility/deprecation note for this feature release in `docs/api/deprecations.md` and `specs/006-add-username-privacy/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies; start immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2; defines MVP cut.
- **Phase 4 (US2)**: Depends on Phase 2; recommended after US1 because post-backfill integrity constraints assume registration flow writes usernames.
- **Phase 5 (US3)**: Depends on Phase 2; can run in parallel with US2 if serializer/view ownership changes are coordinated.
- **Phase 6 (US4)**: Depends on Phase 2 and reuses US1 username validation/persistence behavior.
- **Phase 7 (Polish)**: Depends on completion of all desired user stories.

### User Story Dependencies

- **US1 (P1)**: Independent after foundational completion.
- **US2 (P2)**: Independent after foundational completion; safest sequencing is after US1.
- **US3 (P3)**: Independent after foundational completion.
- **US4 (P4)**: Independent after foundational completion; leverages username validation from US1.

### Within Each User Story

- Write tests first and confirm they fail before implementation.
- Data/model constraints before service logic.
- Service logic before view/endpoint wiring.
- Endpoint implementation before docs/schema updates.

---

## Parallel Opportunities

- **Setup**: T002, T003, and T004 can run in parallel.
- **Foundational**: T008 and T009 can run in parallel.
- **US1**: T012 and T013 can run in parallel.
- **US2**: T019 can run while T020 is prepared (same file merges required before completion).
- **US3**: T025, T026, and T027 can run in parallel.
- **US4**: T032, T033, and T034 can run in parallel.
- **Polish**: T042, T043, and T045 can run in parallel.

---

## Parallel Example: User Story 1

```bash
Task: "T012 [US1] registration validation tests in users/tests/test_registration.py"
Task: "T013 [US1] username uniqueness tests in users/tests/test_registration.py"
```

## Parallel Example: User Story 2

```bash
Task: "T019 [US2] backfill migration tests in users/tests/test_migrations_username_backfill.py"
Task: "T024 [US2] rollout/backfill documentation in specs/006-add-username-privacy/quickstart.md"
```

## Parallel Example: User Story 3

```bash
Task: "T025 [US3] user email-redaction tests in users/tests/test_api_email_visibility.py"
Task: "T027 [US3] profile visibility tests in profiles/tests/test_api_email_visibility.py"
```

## Parallel Example: User Story 4

```bash
Task: "T032 [US4] first-change/cooldown tests in users/tests/test_username_change.py"
Task: "T033 [US4] cooldown configuration tests in users/tests/test_username_change.py"
Task: "T034 [US4] duplicate/format validation tests in users/tests/test_username_change.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Deliver Phase 3 (US1).
3. Validate registration + email/password authentication behavior.
4. Demo/release MVP if required.

### Incremental Delivery

1. Deliver US1 (registration/auth baseline).
2. Deliver US2 (legacy account backfill integrity).
3. Deliver US3 (email privacy projection rules).
4. Deliver US4 (username change cooldown behavior).
5. Complete Phase 7 polish and full gates.

### Parallel Team Strategy

1. Team completes Phases 1-2 together.
2. Split by story after foundational checkpoint:
   - Engineer A: US1/US4 (shared username flow files)
   - Engineer B: US2 (migrations/backfill)
   - Engineer C: US3 (visibility projection)
3. Rejoin for Phase 7 validation and schema publication.

---

## Notes

- [P] tasks indicate different files or independently preparable workstreams.
- Every task includes explicit file path targets.
- Suggested MVP scope: **Phase 1 + Phase 2 + Phase 3 (US1)**.
- Execute all commands via `poetry run` per constitution.
