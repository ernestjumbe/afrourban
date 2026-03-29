---

description: "Task list for application health endpoint"
---

# Tasks: Application Health Endpoint

**Input**: Design documents from `/specs/007-health-endpoint/`  
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED by the constitution and by this feature's success criteria; include unit, integration, and schema/contract coverage for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no unmet dependencies)
- **[Story]**: Which user story this belongs to (`US1`, `US2`, `US3`)
- Every task includes explicit file path targets

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the new Django app surface and feature-specific test/documentation scaffolding.

- [X] T001 Create the `health` app skeleton in `health/__init__.py`, `health/apps.py`, `health/models.py`, `health/selectors.py`, `health/services.py`, `health/serializers.py`, `health/views.py`, `health/urls.py`, and `health/tests/__init__.py`
- [X] T002 Create feature test modules `health/tests/test_services.py`, `health/tests/test_api_health.py`, and `health/tests/test_api_docs.py`
- [X] T003 [P] Add health-endpoint placeholder sections in `docs/api/endpoints.md` and `docs/api/README.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared app registration and API wiring that all user stories depend on.

**⚠️ CRITICAL**: No user story work should begin until this phase is complete.

- [X] T004 Add the `health` app and logger namespace configuration in `afrourban/settings/base.py`
- [X] T005 [P] Import `health.urls.api_v1_urlpatterns` and include them in central `api_urlpatterns` in `afrourban/urls.py`
- [X] T006 [P] Classify `/api/v1/health/` as a public endpoint in `afrourban/api_schema.py`

**Checkpoint**: Foundation complete; feature work can proceed on a stable app/routing base.

---

## Phase 3: User Story 1 - Verify Backend Availability Without Sign-In (Priority: P1) 🎯 MVP

**Goal**: Expose an anonymous, unthrottled health endpoint that returns a simple healthy/non-healthy signal for the running application process.

**Independent Test**: Send unauthenticated requests to `/api/v1/health/` and verify healthy requests return HTTP `200` with `{"status":"healthy"}`, while simulated non-healthy startup/shutdown or internal-failure states return HTTP `503` with `{"status":"unhealthy"}`.

### Tests for User Story 1 (required) ⚠️

> **NOTE: Write these tests FIRST and confirm they fail before implementation**

- [X] T007 [P] [US1] Add application-lifecycle evaluation tests for healthy, unhealthy, startup, and shutdown states in `health/tests/test_services.py`
- [X] T008 [P] [US1] Add API contract tests for anonymous access, `200`/`503` semantics, single-field body, and rate-limit exemption in `health/tests/test_api_health.py`

### Implementation for User Story 1

- [X] T009 [US1] Implement application lifecycle evaluation helpers and healthy/non-healthy mapping in `health/services.py`
- [X] T010 [US1] Implement the single-field health status output serializer in `health/serializers.py`
- [X] T011 [US1] Implement the anonymous, unthrottled `GET /api/v1/health/` API view in `health/views.py`
- [X] T012 [US1] Register the `health/` route export for `/api/v1/health/` in `health/urls.py`

**Checkpoint**: User Story 1 is independently functional and can serve as the MVP release.

---

## Phase 4: User Story 2 - Check Availability Before Frontend Workflows (Priority: P2)

**Goal**: Make the endpoint discoverable and predictable for frontend startup checks through stable schema publication and explicit public documentation.

**Independent Test**: A frontend-style anonymous caller can hit `/api/v1/health/` before sign-in and the public/internal OpenAPI surfaces both describe the endpoint as a public unauthenticated availability check.

### Tests for User Story 2 (required) ⚠️

- [X] T013 [P] [US2] Add API tests proving credentials do not change pre-auth response semantics in `health/tests/test_api_health.py`
- [X] T014 [P] [US2] Add public/internal OpenAPI visibility tests for `/api/v1/health/` in `health/tests/test_api_docs.py`

### Implementation for User Story 2

- [X] T015 [US2] Add drf-spectacular schema metadata for the health endpoint contract in `health/views.py`
- [X] T016 [US2] Publish frontend and monitoring usage notes for `/api/v1/health/` in `docs/api/endpoints.md` and `docs/api/README.md`

**Checkpoint**: User Story 2 is independently testable through anonymous frontend-style checks and generated schema coverage.

---

## Phase 5: User Story 3 - Keep Health Scope Limited to the Application Process (Priority: P3)

**Goal**: Ensure the endpoint ignores external dependency failures, exposes no extra diagnostics, and emits structured observability events for health evaluations.

**Independent Test**: Simulate an unavailable external dependency while the application process still serves requests and verify `/api/v1/health/` remains healthy, returns only the `status` field, and emits one structured log event per evaluation.

### Tests for User Story 3 (required) ⚠️

- [X] T017 [P] [US3] Add service tests proving external dependency failures do not change application health in `health/tests/test_services.py`
- [X] T018 [P] [US3] Add API tests proving responses remain status-only and never expose dependency diagnostics in `health/tests/test_api_health.py`
- [X] T019 [US3] Add structured logging assertions for health evaluations in `health/tests/test_services.py`

### Implementation for User Story 3

- [X] T020 [US3] Refine the application-process-only evaluation rules and dependency exclusions in `health/services.py`
- [X] T021 [US3] Emit structured `health_check_evaluated` logs from `health/services.py` and `health/views.py`
- [X] T022 [US3] Document the application-process-only scope and dependency exclusions in `docs/api/endpoints.md` and `specs/007-health-endpoint/contracts/health-endpoint.md`

**Checkpoint**: User Story 3 is independently verifiable through dependency-exclusion and observability scenarios.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Publish final artifacts and run full-project validation across all stories.

- [X] T023 [P] Regenerate committed schema artifacts in `docs/api/openapi-public.yaml` and `docs/api/openapi-internal.yaml`
- [X] T024 [P] Refresh the final API catalog and runbook text in `docs/api/endpoints.md` and `docs/api/README.md`
- [X] T025 Run `poetry run ruff check .`, `poetry run mypy .`, `poetry run pytest`, and `poetry run python manage.py spectacular --file /tmp/openapi-health-validate.yaml --validate`, then record outcomes in `specs/007-health-endpoint/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies; start immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2 and defines the MVP cut line.
- **Phase 4 (US2)**: Depends on Phase 2; safest after US1 because it documents and validates the live endpoint contract.
- **Phase 5 (US3)**: Depends on Phase 2; safest after US1 because it refines the same service/view behavior.
- **Phase 6 (Polish)**: Depends on completion of all desired user stories.

### User Story Dependencies

- **US1 (P1)**: Independent after foundational completion.
- **US2 (P2)**: Depends on the existence of the US1 endpoint contract and routing.
- **US3 (P3)**: Depends on the US1 endpoint implementation and then tightens its scope and observability behavior.

### Within Each User Story

- Write tests first and confirm they fail before implementation.
- Implement service behavior before endpoint orchestration.
- Implement endpoint behavior before documentation/schema publication.
- Finish each story completely before treating it as shippable.

---

## Parallel Opportunities

- **Setup**: T002 and T003 can run in parallel after T001 creates the app/test directories.
- **Foundational**: T005 and T006 can run in parallel after T004.
- **US1**: T007 and T008 can run in parallel.
- **US2**: T013 and T014 can run in parallel.
- **US3**: T017 and T018 can run in parallel.
- **Polish**: T023 and T024 can run in parallel before T025.

---

## Parallel Example: User Story 1

```bash
Task: "T007 [US1] lifecycle evaluation tests in health/tests/test_services.py"
Task: "T008 [US1] anonymous endpoint contract tests in health/tests/test_api_health.py"
```

## Parallel Example: User Story 2

```bash
Task: "T013 [US2] pre-auth response semantics tests in health/tests/test_api_health.py"
Task: "T014 [US2] public/internal schema visibility tests in health/tests/test_api_docs.py"
```

## Parallel Example: User Story 3

```bash
Task: "T017 [US3] dependency-exclusion service tests in health/tests/test_services.py"
Task: "T018 [US3] status-only response tests in health/tests/test_api_health.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Deliver Phase 3 (US1).
3. Validate anonymous `/api/v1/health/` behavior independently.
4. Demo or release the endpoint as the MVP if needed.

### Incremental Delivery

1. Deliver US1 to establish the core health signal.
2. Deliver US2 to publish and validate frontend-facing discovery/documentation.
3. Deliver US3 to lock in the application-process-only boundary and observability.
4. Finish with Phase 6 publication and quality gates.

### Parallel Team Strategy

1. Team completes Setup and Foundational phases together.
2. After foundational completion:
   - Engineer A: US1 endpoint/service implementation
   - Engineer B: US2 docs/schema tests and publication prep
   - Engineer C: US3 scope/logging tests and service refinements
3. Rejoin for Phase 6 schema regeneration and full validation.

---

## Notes

- [P] tasks indicate different files or independently preparable workstreams.
- Every task includes explicit file path targets.
- Suggested MVP scope: **Phase 1 + Phase 2 + Phase 3 (US1)**.
- Execute all validation commands with `poetry run` per constitution.
