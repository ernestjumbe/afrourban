---

description: "Task list for organization profiles"
---

# Tasks: Organization Profiles

**Input**: Design documents from `/specs/009-organization-profiles/`  
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED by the constitution and by this feature's success criteria; include service, API, routing, and schema coverage for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no unmet dependencies)
- **[Story]**: Which user story this belongs to (`US1`, `US2`, `US3`)
- Every task includes explicit file path targets

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the new app surface and feature-specific test/documentation scaffolding.

- [X] T001 Create the `organizations` app skeleton in `organizations/__init__.py`, `organizations/apps.py`, `organizations/admin.py`, `organizations/models.py`, `organizations/selectors.py`, `organizations/services.py`, `organizations/serializers.py`, `organizations/views.py`, `organizations/urls.py`, `organizations/permissions.py`, and `organizations/tests/__init__.py`
- [X] T002 Create feature test modules `organizations/tests/test_services.py`, `organizations/tests/test_selectors.py`, `organizations/tests/test_api_collection.py`, `organizations/tests/test_api_detail.py`, `organizations/tests/test_api_branding.py`, `organizations/tests/test_api_versioning.py`, and `organizations/tests/test_api_docs.py`
- [X] T003 [P] Add organizations endpoint placeholders in `docs/api/endpoints.md` and `docs/api/README.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared model, app registration, routing, and helpers used by all user stories.

**⚠️ CRITICAL**: No user story work should begin until this phase is complete.

- [X] T004 Add the `organizations` app and `organizations` logger namespace in `afrourban/settings/base.py`
- [X] T005 [P] Define `OrganizationType`, `Organization`, and owner-scoped case-insensitive name uniqueness in `organizations/models.py`
- [X] T006 Create the initial organization schema migration in `organizations/migrations/0001_initial.py`
- [X] T007 [P] Create organization factories and uploaded-image helpers in `organizations/tests/factories.py`
- [X] T008 [P] Implement owner-only organization permission helpers in `organizations/permissions.py`
- [X] T009 [P] Add shared organization collection/detail selector scaffolding in `organizations/selectors.py`
- [X] T010 [P] Add structured organization logging helpers and base write-service scaffolding in `organizations/services.py`
- [X] T011 [P] Import `organizations.urls.api_v1_urlpatterns` into central `api_urlpatterns` in `afrourban/urls.py`

**Checkpoint**: Foundation complete; all user story phases can proceed.

---

## Phase 3: User Story 1 - Create an Organization Profile (Priority: P1) 🎯 MVP

**Goal**: Allow authenticated users to create organization profiles with required metadata, owner assignment, and correct physical-vs-online validation rules.

**Independent Test**: `POST /api/v1/organizations/` with a valid physical or online-only payload returns `201`, stores the authenticated owner, rejects duplicate same-owner names, and rejects physical organizations without an address.

### Tests for User Story 1 (required) ⚠️

> **NOTE: Write these tests FIRST and confirm they fail before implementation**

- [X] T012 [P] [US1] Add service tests for organization creation, same-owner duplicate-name rejection, and physical-address validation in `organizations/tests/test_services.py`
- [X] T013 [P] [US1] Add collection API tests for authenticated organization creation and invalid create payloads in `organizations/tests/test_api_collection.py`

### Implementation for User Story 1

- [X] T014 [P] [US1] Implement organization-create validation and owner assignment in `organizations/services.py`
- [X] T015 [P] [US1] Implement create input and detail output serializers in `organizations/serializers.py`
- [X] T016 [US1] Implement `POST /api/v1/organizations/` with drf-spectacular metadata in `organizations/views.py`
- [X] T017 [US1] Register the collection create route in `organizations/urls.py`
- [X] T018 [US1] Emit structured organization-create success and validation-failure logs in `organizations/services.py` and `organizations/views.py`

**Checkpoint**: User Story 1 is independently functional and defines the MVP cut line.

---

## Phase 4: User Story 2 - Maintain Organization Identity and Branding (Priority: P2)

**Goal**: Let organization owners update profile metadata and manage logo/cover branding while blocking non-owner writes.

**Independent Test**: The owner can patch organization metadata, toggle online-only mode with correct address behavior, upload/replace/delete logo and cover images, and non-owner write attempts return `403`.

### Tests for User Story 2 (required) ⚠️

- [X] T019 [P] [US2] Add service tests for metadata updates, online-only address clearing, and owner-only write enforcement in `organizations/tests/test_services.py`
- [X] T020 [P] [US2] Add detail API tests for owner PATCH updates and non-owner rejection in `organizations/tests/test_api_detail.py`
- [X] T021 [P] [US2] Add branding API tests for logo/cover upload, replacement, deletion, and file validation in `organizations/tests/test_api_branding.py`

### Implementation for User Story 2

- [X] T022 [P] [US2] Implement organization update service rules for metadata changes and presence transitions in `organizations/services.py`
- [X] T023 [P] [US2] Implement patch input and branding upload serializers in `organizations/serializers.py`
- [X] T024 [US2] Implement owner-only `PATCH /api/v1/organizations/{organization_id}/` and branding upload/delete views in `organizations/views.py`
- [X] T025 [US2] Register detail patch and branding routes in `organizations/urls.py`
- [X] T026 [US2] Emit structured organization-update and branding-mutation logs in `organizations/services.py` and `organizations/views.py`

**Checkpoint**: User Story 2 is independently testable against an existing seeded organization record.

---

## Phase 5: User Story 3 - View Organization Profiles Separately from People (Priority: P3)

**Goal**: Let authenticated users browse organization collection/detail endpoints that clearly expose organization-specific data, filtering, and pagination without mixing in person-profile behavior.

**Independent Test**: `GET /api/v1/organizations/` and `GET /api/v1/organizations/{organization_id}/` return organization-only fields, owner/type/presence filters and pagination work, online-only organizations show no physical address, and the organizations endpoints appear only in the internal `/api/v1/` schema.

### Tests for User Story 3 (required) ⚠️

- [X] T027 [P] [US3] Add selector tests for organization search, filtering, sorting, and owner-scope reads in `organizations/tests/test_selectors.py`
- [X] T028 [P] [US3] Add collection/detail API tests for organization-only payloads, pagination, and online-only display behavior in `organizations/tests/test_api_collection.py` and `organizations/tests/test_api_detail.py`
- [X] T029 [P] [US3] Add routing and schema visibility tests for `/api/v1/organizations/` in `organizations/tests/test_api_versioning.py` and `organizations/tests/test_api_docs.py`

### Implementation for User Story 3

- [X] T030 [P] [US3] Implement filtered organization list/detail selectors in `organizations/selectors.py`
- [X] T031 [P] [US3] Implement organization list/detail output serializers with branding URLs and owner ids in `organizations/serializers.py`
- [X] T032 [US3] Implement `GET /api/v1/organizations/` and `GET /api/v1/organizations/{organization_id}/` with the documented pagination envelope in `organizations/views.py`
- [X] T033 [US3] Register authenticated collection/detail read routes in `organizations/urls.py`
- [X] T034 [US3] Publish organizations endpoint behavior and viewer guidance in `docs/api/endpoints.md` and `docs/api/README.md`

**Checkpoint**: User Story 3 is independently verifiable through authenticated browsing and schema visibility checks.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finish admin/support surfaces, publish schema artifacts, and run full validation across all stories.

- [X] T035 [P] Register the `Organization` model in Django admin in `organizations/admin.py`
- [X] T036 [P] Regenerate committed schema artifacts in `docs/api/openapi-public.yaml` and `docs/api/openapi-internal.yaml`
- [X] T037 Run `poetry run ruff check .`, `poetry run mypy .`, `poetry run pytest`, and `poetry run python manage.py spectacular --settings=afrourban.settings.test --validate --file /tmp/openapi-009-validate.yaml`, then record results in `specs/009-organization-profiles/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies; start immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2 and defines the MVP cut line.
- **Phase 4 (US2)**: Depends on Phase 2; safest after US1 because it extends the shared organization serializers/views with owner-only mutations.
- **Phase 5 (US3)**: Depends on Phase 2; can proceed after US1, but parallel work with US2 requires coordination on `organizations/serializers.py`, `organizations/views.py`, and `organizations/urls.py`.
- **Phase 6 (Polish)**: Depends on completion of all desired user stories.

### User Story Dependencies

- **US1 (P1)**: Independent after foundational completion.
- **US2 (P2)**: Independent after foundational completion with seeded organization data; recommended after US1 for smoother route/view integration.
- **US3 (P3)**: Independent after foundational completion with seeded organization data; recommended after US1 because it adds read behavior to the same route surface.

### Within Each User Story

- Write tests first and confirm they fail before implementation.
- Implement service and serializer changes before view orchestration.
- Implement view behavior before route wiring and documentation publication.
- Finish each story completely before treating it as shippable.

---

## Parallel Opportunities

- **Setup**: T002 and T003 can run in parallel after T001.
- **Foundational**: T008, T009, T010, and T011 can run in parallel after T004-T005 establish the app/model base.
- **US1**: T012 and T013 can run in parallel; T014 and T015 can run in parallel after the tests are in place.
- **US2**: T019, T020, and T021 can run in parallel; T022 and T023 can run in parallel after those tests are written.
- **US3**: T027, T028, and T029 can run in parallel; T030 and T031 can run in parallel after those tests are written.
- **Polish**: T035 and T036 can run in parallel before T037.

---

## Parallel Example: User Story 1

```bash
Task: "T012 [US1] organization creation service tests in organizations/tests/test_services.py"
Task: "T013 [US1] collection create API tests in organizations/tests/test_api_collection.py"
```

## Parallel Example: User Story 2

```bash
Task: "T020 [US2] owner patch API tests in organizations/tests/test_api_detail.py"
Task: "T021 [US2] branding API tests in organizations/tests/test_api_branding.py"
```

## Parallel Example: User Story 3

```bash
Task: "T027 [US3] selector filtering/sorting tests in organizations/tests/test_selectors.py"
Task: "T029 [US3] routing/schema visibility tests in organizations/tests/test_api_versioning.py and organizations/tests/test_api_docs.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Deliver Phase 3 (US1).
3. Validate authenticated organization creation independently.
4. Demo or release the create flow as the MVP if needed.

### Incremental Delivery

1. Deliver US1 to establish the organization resource and create flow.
2. Deliver US2 to unlock owner-side maintenance and branding.
3. Deliver US3 to publish the authenticated browsing experience and schema coverage.
4. Finish with Phase 6 admin/schema/validation tasks.

### Parallel Team Strategy

1. Team completes Setup and Foundational phases together.
2. After foundational completion:
   - Engineer A: US1 create flow
   - Engineer B: US2 update and branding flow
   - Engineer C: US3 read APIs and schema coverage
3. Coordinate merges carefully for `organizations/serializers.py`, `organizations/views.py`, and `organizations/urls.py`.
4. Rejoin for Phase 6 schema publication and full validation.

---

## Notes

- [P] tasks indicate different files or independently preparable workstreams.
- Every task includes explicit file path targets.
- Suggested MVP scope: **Phase 1 + Phase 2 + Phase 3 (US1)**.
- Execute all validation commands with `poetry run` per constitution.
