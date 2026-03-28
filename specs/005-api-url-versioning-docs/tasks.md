---

description: "Task list for API URL versioning and documentation"
---

# Tasks: API URL Versioning and Documentation

**Input**: Design documents from `/specs/005-api-url-versioning-docs/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED by the constitution. Include unit, integration, and contract tests for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Every task includes concrete file path(s)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install tooling and create baseline files needed by all stories.

- [X] T001 Add `drf-spectacular` dependency configuration in `pyproject.toml` and `poetry.lock`
- [X] T002 Create deprecation baseline docs in `docs/api/deprecations.md` and `docs/api/deprecations.yaml`
- [X] T003 [P] Create versioning test modules `users/tests/test_api_versioning.py` and `profiles/tests/test_api_versioning.py`
- [X] T004 [P] Create docs/deprecation test modules `users/tests/test_api_docs.py`, `profiles/tests/test_api_docs.py`, and `users/tests/test_api_deprecations.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared routing, schema, and policy infrastructure that blocks all stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 Configure DRF schema backend and `SPECTACULAR_SETTINGS` defaults in `afrourban/settings/base.py`
- [X] T006 Implement schema visibility and endpoint classification helpers in `afrourban/api_schema.py`
- [X] T007 Add API documentation route scaffolding for public/internal schema+UI in `afrourban/urls.py`
- [X] T008 [P] Add version-exported URL pattern lists for users and profiles in `users/urls.py` and `profiles/urls.py`
- [X] T009 [P] Implement 90-day deprecation policy validator utilities in `afrourban/api_governance.py`
- [X] T010 Add shared deprecation fixture helpers in `users/tests/factories.py`

**Checkpoint**: Foundation ready; user story implementation can now proceed.

---

## Phase 3: User Story 1 - Consume Stable Versioned APIs (Priority: P1) 🎯 MVP

**Goal**: Expose all active endpoints under canonical `/api/v1/` and remove unversioned legacy routes.

**Independent Test**: All contract-listed endpoints resolve under `/api/v1/`; legacy `/api/auth/*`, `/api/admin/users/*`, and `/api/profiles/*` routes are unavailable.

### Tests for User Story 1 (required) ⚠️

- [X] T011 [P] [US1] Add contract tests for users/admin `/api/v1/` route inventory in `users/tests/test_api_versioning.py`
- [X] T012 [P] [US1] Add contract tests for profile `/api/v1/` route inventory in `profiles/tests/test_api_versioning.py`
- [X] T013 [US1] Add legacy unversioned route rejection tests in `users/tests/test_api_versioning.py`

### Implementation for User Story 1

- [X] T014 [P] [US1] Refactor users route groups for version-aware includes in `users/urls.py`
- [X] T015 [P] [US1] Refactor profile route groups for version-aware includes in `profiles/urls.py`
- [X] T016 [US1] Register complete `/api/v1/` inventory in `api_urlpatterns` and remove legacy includes in `afrourban/urls.py`
- [X] T017 [US1] Update canonical versioned routing comments/docstrings in `afrourban/urls.py`, `users/urls.py`, and `profiles/urls.py`

**Checkpoint**: User Story 1 is independently testable and shippable as MVP.

---

## Phase 4: User Story 2 - Discover Complete API Documentation (Priority: P2)

**Goal**: Publish complete OpenAPI documentation with public/internal visibility split.

**Independent Test**: Internal docs include all active endpoints; public docs include only public endpoints and exclude restricted/admin routes.

### Tests for User Story 2 (required) ⚠️

- [X] T018 [P] [US2] Add contract tests for internal schema endpoint completeness in `users/tests/test_api_docs.py`
- [X] T019 [P] [US2] Add contract tests for public schema visibility filtering in `profiles/tests/test_api_docs.py`
- [X] T020 [US2] Add integration tests for docs access control on `/api/v1/docs/public/` and `/api/v1/docs/internal/` in `users/tests/test_api_docs.py`

### Implementation for User Story 2

- [X] T021 [US2] Implement public/internal schema and UI routes in `afrourban/urls.py`
- [X] T022 [US2] Implement schema filtering pipeline for route scopes in `afrourban/api_schema.py`
- [X] T023 [US2] Normalize users endpoint schema tags and permission metadata in `users/views.py` and `users/urls.py`
- [X] T024 [US2] Normalize profiles endpoint schema tags and permission metadata in `profiles/views.py` and `profiles/urls.py`
- [X] T025 [US2] Publish endpoint inventory and permission matrix in `docs/api/endpoints.md`

**Checkpoint**: User Story 2 docs are independently consumable and verifiable.

---

## Phase 5: User Story 3 - Plan and Communicate Deprecations (Priority: P3)

**Goal**: Enforce deprecation policy completeness and 90-day notice rules.

**Independent Test**: Each deprecation entry includes `deprecation_date`, `removal_date`, and `migration_path`; validation fails if notice window is <90 days.

### Tests for User Story 3 (required) ⚠️

- [X] T026 [US3] Add deprecation field and 90-day window unit tests in `users/tests/test_api_deprecations.py`
- [X] T027 [US3] Add integration test for internal docs deprecation metadata presence in `users/tests/test_api_docs.py`

### Implementation for User Story 3

- [X] T028 [US3] Define machine-readable deprecation registry structure in `docs/api/deprecations.yaml`
- [X] T029 [US3] Publish human-readable deprecation policy and migration guidance in `docs/api/deprecations.md`
- [X] T030 [US3] Wire deprecation validation into schema/governance helpers in `afrourban/api_schema.py` and `afrourban/api_governance.py`
- [X] T031 [US3] Implement deprecation validation command in `users/management/commands/validate_api_deprecations.py`
- [X] T032 [US3] Add management package initializers in `users/management/__init__.py` and `users/management/commands/__init__.py`

**Checkpoint**: User Story 3 governance policy is independently testable and release-ready.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening and release artifacts across all stories.

- [X] T033 [P] Regenerate and store OpenAPI artifacts in `docs/api/openapi-public.yaml` and `docs/api/openapi-internal.yaml`
- [X] T034 [P] Add API verification runbook for route/docs/deprecation checks in `docs/api/README.md`
- [X] T035 Validate quickstart workflow and record outcomes in `specs/005-api-url-versioning-docs/quickstart.md`
- [X] T036 Run full quality gates and record command outputs/remediation notes in `specs/005-api-url-versioning-docs/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies; start immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2; MVP cut line.
- **Phase 4 (US2)**: Depends on Phase 3 to document finalized versioned route inventory.
- **Phase 5 (US3)**: Depends on Phase 4 to validate deprecation metadata in published docs.
- **Phase 6 (Polish)**: Depends on completion of desired user stories.

### User Story Dependencies

- **US1 (P1)**: Independent after foundational setup.
- **US2 (P2)**: Depends on US1 route stabilization.
- **US3 (P3)**: Depends on US2 documentation publication pipeline.

### Within Each User Story

- Tests first and failing before implementation completion
- Routing/model metadata before schema filtering where applicable
- Schema/deprecation publication before final verification

---

## Parallel Opportunities

- **Setup**: T003 and T004 can run in parallel.
- **Foundational**: T008 and T009 can run in parallel after T005-T007.
- **US1**: T011 and T012 can run in parallel; T014 and T015 can run in parallel.
- **US2**: T018 and T019 can run in parallel.
- **Polish**: T033 and T034 can run in parallel.

---

## Parallel Example: User Story 1

```bash
# Parallel contract tests
Task: "T011 [US1] users route inventory tests in users/tests/test_api_versioning.py"
Task: "T012 [US1] profiles route inventory tests in profiles/tests/test_api_versioning.py"

# Parallel route refactors
Task: "T014 [US1] users URL refactor in users/urls.py"
Task: "T015 [US1] profiles URL refactor in profiles/urls.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Complete Phase 1 and Phase 2.
2. Deliver Phase 3 (US1).
3. Validate `/api/v1/` reachability and legacy route removal.
4. Demo/release MVP if needed.

### Incremental Delivery

1. Deliver US1 (versioned routing) as stable base.
2. Add US2 (documentation completeness and visibility split).
3. Add US3 (deprecation governance enforcement).
4. Complete Phase 6 polish.

### Team Parallel Strategy

1. Engineer A: URL migration (US1).
2. Engineer B: Schema/docs split (US2).
3. Engineer C: Deprecation policy tooling (US3).
4. Integrate during Phase 6 with full gates.

---

## Notes

- [P] tasks are limited to different files with no unmet dependencies.
- Story labels map directly to clarified user stories in `spec.md`.
- Every task includes concrete file path targets.
- Suggested MVP scope: **Phase 1 + Phase 2 + Phase 3 (US1)**.
