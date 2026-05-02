---

description: "Task list for events app"
---

# Tasks: Events App

**Input**: Design documents from `/specs/010-add-events-app/`  
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED by the constitution and by this feature's success criteria; include service, API, routing, and schema coverage for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no unmet dependencies)
- **[Story]**: Which user story this belongs to (`US1`, `US2`, `US3`)
- Every task includes explicit file path targets

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the new app surface and feature-specific test/documentation scaffolding.

- [X] T001 Create the `events` app skeleton in `events/__init__.py`, `events/apps.py`, `events/admin.py`, `events/models.py`, `events/selectors.py`, `events/services.py`, `events/serializers.py`, `events/views.py`, `events/urls.py`, `events/permissions.py`, and `events/tests/__init__.py`
- [X] T002 Create feature test modules `events/tests/test_services.py`, `events/tests/test_selectors.py`, `events/tests/test_api_create.py`, `events/tests/test_api_detail.py`, `events/tests/test_api_cover.py`, `events/tests/test_api_versioning.py`, and `events/tests/test_api_docs.py`
- [X] T003 [P] Add events endpoint placeholder notes in `docs/api/endpoints.md` and `docs/api/README.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared model, app registration, routing, and helpers used by all user stories.

**⚠️ CRITICAL**: No user story work should begin until this phase is complete.

- [X] T004 Add the `events` app and `events` logger namespace in `afrourban/settings/base.py`
- [X] T005 [P] Define `EventCategory`, `EventLocationType`, `Event`, and `EventAuditEntry` invariants in `events/models.py`
- [X] T006 Create the initial events schema migration in `events/migrations/0001_initial.py`
- [X] T007 [P] Create event factories, payload builders, and uploaded-image helpers in `events/tests/factories.py`
- [X] T008 [P] Implement event write-access helpers for personal vs organization ownership in `events/permissions.py`
- [X] T009 [P] Add shared event detail selector scaffolding in `events/selectors.py`
- [X] T010 [P] Add shared event normalization, location validation, audit-helper, and structured logging scaffolding in `events/services.py`
- [X] T011 [P] Import `events.urls.api_v1_urlpatterns` into central `api_urlpatterns` in `afrourban/urls.py`

**Checkpoint**: Foundation complete; all user story phases can proceed.

---

## Phase 3: User Story 1 - Create a Personal Event (Priority: P1) 🎯 MVP

**Goal**: Allow authenticated users to create personal events with valid schedule, category defaulting, and physical-vs-web location validation.

**Independent Test**: `POST /api/v1/events/` with a valid personal-event payload returns `201`, stores the event under the authenticated user, defaults category to `other` when omitted, accepts valid web or physical locations, and rejects invalid schedule or location payloads.

### Tests for User Story 1 (required) ⚠️

> **NOTE: Write these tests FIRST and confirm they fail before implementation**

- [X] T012 [P] [US1] Add service tests for personal-event creation, category defaulting, schedule validation, and physical-vs-web location validation in `events/tests/test_services.py`
- [X] T013 [P] [US1] Add create API tests for authenticated personal-event creation and invalid personal payloads in `events/tests/test_api_create.py`

### Implementation for User Story 1

- [X] T014 [P] [US1] Implement personal-event normalization and create rules in `events/services.py`
- [X] T015 [P] [US1] Implement personal-event create input serializers and event detail output serializers in `events/serializers.py`
- [X] T016 [US1] Implement `POST /api/v1/events/` for personal events with drf-spectacular metadata in `events/views.py`
- [X] T017 [US1] Register the collection create route in `events/urls.py`
- [X] T018 [US1] Emit structured personal-event create success and validation-failure logs in `events/services.py` and `events/views.py`

**Checkpoint**: User Story 1 is independently functional and defines the MVP cut line.

---

## Phase 4: User Story 2 - Create an Organization Event (Priority: P2)

**Goal**: Allow organization owners to create events on behalf of owned organizations while blocking non-owners.

**Independent Test**: `POST /api/v1/events/` with an owned `organization_id` returns `201` and links the event to that organization, while the same request from a non-owner returns `403`.

### Tests for User Story 2 (required) ⚠️

- [X] T019 [P] [US2] Add service tests for organization-event creation and owner-only organization authorization in `events/tests/test_services.py`
- [X] T020 [P] [US2] Add create API tests for owned-organization event creation and non-owner rejection in `events/tests/test_api_create.py`

### Implementation for User Story 2

- [X] T021 [P] [US2] Implement organization-organizer resolution and ownership checks for event creation in `events/services.py`
- [X] T022 [P] [US2] Extend create/detail serializers to accept organization-owned organizer context in `events/serializers.py`
- [X] T023 [US2] Extend `POST /api/v1/events/` to create organization-owned events and return organizer metadata in `events/views.py`
- [X] T024 [US2] Emit structured organization-event create success and permission-denied logs in `events/services.py` and `events/views.py`

**Checkpoint**: User Story 2 is independently testable with seeded organization data.

---

## Phase 5: User Story 3 - Maintain Event Details with Audit History (Priority: P3)

**Goal**: Let authorized organizers read, update, and manage event details while preserving immutable audit history for title, start time, end time, and location changes.

**Independent Test**: `GET /api/v1/events/{event_id}/` returns the current event state, `PATCH /api/v1/events/{event_id}/` allows only authorized organizers to update it, tracked-field changes create immutable audit rows, organizer context remains immutable, and cover-image upload/delete flows respect the same ownership rules.

### Tests for User Story 3 (required) ⚠️

- [X] T025 [P] [US3] Add selector tests for event detail loading with organizer relations in `events/tests/test_selectors.py`
- [X] T026 [P] [US3] Add service tests for audited metadata updates, location transitions, organizer immutability, and unauthorized write rejection in `events/tests/test_services.py`
- [X] T027 [P] [US3] Add detail API tests for `GET`/`PATCH` event maintenance flows, tracked-field audit behavior, and unauthorized update rejection in `events/tests/test_api_detail.py`
- [X] T028 [P] [US3] Add cover-image API tests for upload, replacement, deletion, and file validation in `events/tests/test_api_cover.py`
- [X] T029 [P] [US3] Add routing and schema visibility tests for `/api/v1/events/` in `events/tests/test_api_versioning.py` and `events/tests/test_api_docs.py`

### Implementation for User Story 3

- [X] T030 [P] [US3] Implement audited event detail selectors with organizer relation loading in `events/selectors.py`
- [X] T031 [P] [US3] Implement patch input, nested location, and cover output serializers in `events/serializers.py`
- [X] T032 [US3] Implement event update rules, immutable audit-entry creation, and cover-image mutation services in `events/services.py`
- [X] T033 [US3] Implement `GET`/`PATCH /api/v1/events/{event_id}/` and `POST`/`DELETE /api/v1/events/{event_id}/cover/` with drf-spectacular metadata in `events/views.py`
- [X] T034 [US3] Register authenticated detail and cover routes in `events/urls.py`
- [X] T035 [US3] Publish events endpoint behavior and authenticated-only visibility notes in `docs/api/endpoints.md` and `docs/api/README.md`
- [X] T036 [US3] Emit structured event-update, audit-write, and cover-mutation logs in `events/services.py` and `events/views.py`

**Checkpoint**: User Story 3 is independently verifiable through authorized maintenance flows and audit persistence checks.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finish admin/support surfaces, publish schema artifacts, and run full validation across all stories.

- [X] T037 [P] Register the `Event` and `EventAuditEntry` models in Django admin in `events/admin.py`
- [X] T038 [P] Regenerate committed schema artifacts in `docs/api/openapi-public.yaml` and `docs/api/openapi-internal.yaml`
- [X] T039 Run `poetry run ruff check .`, `poetry run mypy .`, `poetry run pytest`, and `poetry run python manage.py spectacular --settings=afrourban.settings.test --validate --file /tmp/openapi-010-validate.yaml`, then record results in `specs/010-add-events-app/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies; start immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2 and defines the MVP cut line.
- **Phase 4 (US2)**: Depends on Phase 2; recommended after US1 because it extends the same create service, serializers, and collection POST view.
- **Phase 5 (US3)**: Depends on Phase 2; recommended after US1 because it builds on the shared event model and serializer surface, but can proceed in parallel with US2 with coordination on `events/services.py`, `events/serializers.py`, and `events/views.py`.
- **Phase 6 (Polish)**: Depends on completion of all desired user stories.

### User Story Dependencies

- **US1 (P1)**: Independent after foundational completion.
- **US2 (P2)**: Independent after foundational completion with seeded organization data; recommended after US1 for smoother POST-route integration.
- **US3 (P3)**: Independent after foundational completion with seeded event data; recommended after US1 because it adds detail/update behavior to the same event resource.

### Within Each User Story

- Write tests first and confirm they fail before implementation.
- Implement service and serializer changes before view orchestration.
- Implement view behavior before route wiring and documentation publication.
- Finish each story completely before treating it as shippable.

---

## Parallel Opportunities

- **Setup**: T002 and T003 can run in parallel after T001.
- **Foundational**: T007, T008, T009, T010, and T011 can run in parallel after T004-T005 establish the app/model base.
- **US1**: T012 and T013 can run in parallel; T014 and T015 can run in parallel after those tests are written.
- **US2**: T019 and T020 can run in parallel; T021 and T022 can run in parallel after those tests are written.
- **US3**: T025, T026, T027, T028, and T029 can run in parallel; T030 and T031 can run in parallel after those tests are written.
- **Polish**: T037 and T038 can run in parallel before T039.

---

## Parallel Example: User Story 1

```bash
Task: "T012 [US1] personal-event creation service tests in events/tests/test_services.py"
Task: "T013 [US1] personal-event create API tests in events/tests/test_api_create.py"
```

## Parallel Example: User Story 2

```bash
Task: "T019 [US2] organization-event creation service tests in events/tests/test_services.py"
Task: "T020 [US2] organization-event create API tests in events/tests/test_api_create.py"
```

## Parallel Example: User Story 3

```bash
Task: "T027 [US3] detail PATCH audit tests in events/tests/test_api_detail.py"
Task: "T029 [US3] routing/schema visibility tests in events/tests/test_api_versioning.py and events/tests/test_api_docs.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Deliver Phase 3 (US1).
3. Validate authenticated personal-event creation independently.
4. Demo or release the personal-event create flow as the MVP if needed.

### Incremental Delivery

1. Deliver US1 to establish the base event resource and personal create flow.
2. Deliver US2 to add organization-owned creation on the same resource.
3. Deliver US3 to unlock detail maintenance, audit retention, and cover-image management.
4. Finish with Phase 6 admin/schema/validation tasks.

### Parallel Team Strategy

1. Team completes Setup and Foundational phases together.
2. After foundational completion:
   - Engineer A: US1 personal-event creation flow
   - Engineer B: US2 organization-owned creation flow
   - Engineer C: US3 detail/update/audit flow
3. Coordinate merges carefully for `events/services.py`, `events/serializers.py`, and `events/views.py`.
4. Rejoin for Phase 6 schema publication and full validation.

---

## Notes

- [P] tasks indicate different files or independently preparable workstreams.
- Every task includes explicit file path targets.
- Suggested MVP scope: **Phase 1 + Phase 2 + Phase 3 (US1)**.
- Execute all validation commands with `poetry run` per constitution.
