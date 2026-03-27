# Tasks: Age Verification Field

**Input**: Design documents from `/specs/002-age-verification-field/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

**Tests**: Not explicitly requested in the feature specification. Test tasks are omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Dependency**: This feature EXTENDS feature 001 (Custom User & Profile Management). Profile and Policy models already exist.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md structure:
- `profiles/` - Profile app (extended)
- `users/` - User app (JWT claims extended)
- `afrourban/` - Project settings and core

---

## Phase 1: Setup (Verify Prerequisites)

**Purpose**: Ensure feature 001 is in place and project is ready for extension

- [X] T001 Verify feature 001 branch is merged and Profile model exists with date_of_birth field
- [X] T002 Verify Policy model exists with conditions JSONField
- [X] T003 [P] Verify JWT claims builder exists in users/claims.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure for age verification that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create AgeVerificationStatus TextChoices enum in profiles/models.py (unverified, self_declared, pending, verified, failed)
- [X] T005 Add age_verification_status field to Profile model (CharField, default='unverified')
- [X] T006 Add age_verified_at field to Profile model (DateTimeField, null, blank)
- [X] T007 Create migration for age verification fields: `poetry run python manage.py makemigrations profiles --name add_age_verification_fields`
- [X] T008 Apply migration: `poetry run python manage.py migrate`

**Checkpoint**: Foundation ready - Profile model now has age verification fields

---

## Phase 3: User Story 1 - Date of Birth Collection (Priority: P1) 🎯 MVP

**Goal**: Allow users to provide date of birth with validation and display calculated age

**Independent Test**: Login, go to profile, enter valid DOB, verify it is saved, verify age is calculated and displayed correctly

### Implementation for User Story 1

- [X] T009 [P] [US1] Add date_of_birth validators in profiles/models.py (not in future, not > 120 years ago)
- [X] T010 [P] [US1] Add `age` computed property to Profile model in profiles/models.py (calculate from date_of_birth)
- [X] T011 [US1] Update ProfileInputSerializer in profiles/serializers.py to include date_of_birth with validation
- [X] T012 [US1] Update ProfileOutputSerializer in profiles/serializers.py to include age (read-only), date_of_birth (own profile only)
- [X] T013 [US1] Update profile_update service in profiles/services.py to handle date_of_birth updates
- [X] T014 [US1] Ensure ProfileMeView returns age field for GET /api/profiles/me/

**Checkpoint**: User Story 1 complete - users can provide DOB and see their calculated age

---

## Phase 4: User Story 2 - Age Verification Status Tracking (Priority: P2)

**Goal**: Track verification status and auto-transition when DOB is provided

**Independent Test**: Create new profile (verify status=unverified), provide DOB (verify status=self_declared with timestamp), update DOB (verify timestamp is reset)

### Implementation for User Story 2

- [X] T015 [P] [US2] Add `age_verified` computed property to Profile model in profiles/models.py (bool: status != unverified)
- [X] T016 [US2] Update profile_update service in profiles/services.py to transition status unverified→self_declared when DOB provided
- [X] T017 [US2] Update profile_update service to reset age_verified_at timestamp when DOB is updated
- [X] T018 [US2] Update ProfileOutputSerializer to include age_verification_status, age_verified_at
- [X] T019 [US2] Update ProfilePublicSerializer (for /api/profiles/{user_id}/) to include age, age_verified (NOT date_of_birth)
- [X] T020 [US2] Update AdminUserDetailSerializer in users/serializers.py to show age_verification_status, age_verified_at

**Checkpoint**: User Story 2 complete - verification status is tracked and transitions correctly

---

## Phase 5: User Story 3 - Minimum Age Policy Enforcement (Priority: P3)

**Goal**: Define minimum age in policies and enforce age restrictions

**Independent Test**: Create policy with minimum_age=18, test with user age 17 (denied), test with user without DOB (denied), test with user age 19 (allowed)

### Implementation for User Story 3

- [X] T021 [P] [US3] Add evaluate_minimum_age function in profiles/services.py (check profile.age >= minimum_age)
- [X] T022 [US3] Update policy_evaluate service in profiles/services.py to include minimum_age condition check
- [X] T023 [US3] Update policy_evaluate to return reason codes: minimum_age_not_met, age_unknown
- [X] T024 [US3] Extend users/claims.py to include age_verification object in JWT (age, status, verified_at)
- [X] T025 [US3] Update CustomTokenObtainPairSerializer to include age_verification in token response
- [X] T026 [P] [US3] Create PolicyCheckSerializer in profiles/serializers.py for policy check response
- [X] T027 [US3] Create PolicyCheckView in profiles/views.py (GET /api/profiles/policies/{policy_id}/check/)
- [X] T028 [US3] Add policy check URL route in profiles/urls.py

**Checkpoint**: User Story 3 complete - age-restricted policies are enforced

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation

- [X] T029 [P] Ensure date_of_birth is NOT included in ProfilePublicSerializer (privacy compliance FR-013)
- [X] T030 [P] Ensure date_of_birth is NOT included in JWT claims (privacy compliance)
- [X] T031 Add structlog audit logging for age_verification_status changes in profiles/services.py
- [X] T032 Run quickstart.md validation (verify all curl commands work)
- [X] T033 Update ProfileAdmin in profiles/admin.py to display age_verification_status, age_verified_at

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Verify feature 001 exists - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - US1 (P1): Can start after Foundational
  - US2 (P2): Depends on US1 (needs DOB handling from US1)
  - US3 (P3): Can start after Foundational, but T024-T025 depend on US2 (status field)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - Core DOB functionality
- **User Story 2 (P2)**: Depends on US1 - Status tracking builds on DOB handling
- **User Story 3 (P3)**: Mostly independent, but JWT claims need status from US2

### Within Each User Story

- Model changes before serializers
- Serializers before services (input validation)
- Services before views
- Views before URL routes

### Parallel Opportunities

- Foundational: T004-T006 can run in parallel
- US1: T009-T010 can run in parallel
- US3: T021 and T026 can run in parallel
- Polish: T029-T030 can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup verification
2. Complete Phase 2: Foundational fields
3. Complete Phase 3: User Story 1 (DOB Collection)
4. **STOP and VALIDATE**: Users can provide DOB, see age
5. Deploy/demo if ready - Basic age capture working

### Incremental Delivery

1. Setup + Foundational → Fields exist in database
2. Add US1 (DOB Collection) → MVP! Users can enter DOB
3. Add US2 (Status Tracking) → Admin can see verification status
4. Add US3 (Policy Enforcement) → Age-gating works end-to-end
5. Each story adds value without breaking previous stories

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- HackSoftware Django Styleguide: services for writes, selectors for reads
- Age calculated dynamically (research.md decision) - not stored
- date_of_birth NEVER in public APIs or JWT (FR-013 privacy requirement)
- Reserved status values (pending, verified, failed) are defined but not implemented - future document verification feature
