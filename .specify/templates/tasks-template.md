---

description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED by the constitution. Include pytest,
Vitest, Playwright, integration, and contract tests as applicable for
each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: backend Django apps at repository root, frontend Next.js
      app at `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

<!-- 
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.
  
  The /speckit.tasks command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Feature requirements from plan.md
  - Entities from data-model.md
  - Endpoints from contracts/
  
  Tasks MUST be organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment
  
  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize [language] project with [framework] dependencies
- [ ] T003 [P] Configure linting and formatting tools

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [ ] T004 Setup database schema and migrations framework
- [ ] T005 [P] Implement authentication/authorization framework
- [ ] T006 [P] Setup API routing and middleware structure with
      `/api/v{n}/` version namespaces
- [ ] T007 Create base models/entities that all stories depend on
- [ ] T008 Configure error handling and logging infrastructure
- [ ] T009 Configure `drf-spectacular` OpenAPI 3.0+ schema generation
      and validation
- [ ] T010 Register all API route groups in `api_urlpatterns` in main
      `urls.py` and include them under `/api/`
- [ ] T011 Define deprecation policy format (deprecation date, removal
      date, migration path) for affected API versions
- [ ] T012 [P] Create `frontend/src/app/` route structure, shared
      component/layout directories, and `frontend/src/middleware.ts`
      when frontend work is in scope
- [ ] T013 [P] Configure Auth.js v5 credentials flow, token refresh,
      and protected route middleware when frontend work is in scope
- [ ] T014 [P] Configure Zod environment validation, TypeScript strict
      mode, ESLint `next/core-web-vitals`, Vitest, Playwright, and
      standalone Next.js build when frontend work is in scope
- [ ] T015 [P] Select the matching AfroUrban Design 4 recipe and shared
      component patterns from `guide/RECIPES.md` and
      `guide/COMPONENT_GUIDE.md` when frontend work is in scope

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - [Title] (Priority: P1) 🎯 MVP

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 1 (required) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T016 [P] [US1] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T017 [P] [US1] Integration test for [user journey] in tests/integration/test_[name].py
- [ ] T018 [P] [US1] Vitest coverage for the affected frontend route,
      server action, or shared schema in frontend tests when frontend is
      in scope

### Implementation for User Story 1

- [ ] T019 [P] [US1] Create [Entity1] model in src/models/[entity1].py
- [ ] T020 [P] [US1] Create [Entity2] model in src/models/[entity2].py
- [ ] T021 [US1] Implement [Service] in src/services/[service].py (depends on T019, T020)
- [ ] T022 [US1] Implement [endpoint/feature] in src/[location]/[file].py
      under a versioned API path
- [ ] T023 [US1] Add validation and error handling
- [ ] T024 [US1] Add logging for user story 1 operations
- [ ] T025 [US1] Update OpenAPI schema output and deprecation metadata
      (if applicable)
- [ ] T026 [US1] Implement the required App Router segment, Server
      Component data fetch, Server Action, or Route Handler in
      `frontend/src/app/...` when frontend is in scope
- [ ] T027 [US1] Apply the selected Design 4 recipe, page shell, and
      documented component patterns for the user-facing UI when frontend
      is in scope

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 2 (required) ⚠️

- [ ] T028 [P] [US2] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T029 [P] [US2] Integration test for [user journey] in tests/integration/test_[name].py
- [ ] T030 [P] [US2] Vitest or Playwright coverage for the affected
      frontend flow when frontend is in scope

### Implementation for User Story 2

- [ ] T031 [P] [US2] Create [Entity] model in src/models/[entity].py
- [ ] T032 [US2] Implement [Service] in src/services/[service].py
- [ ] T033 [US2] Implement [endpoint/feature] in src/[location]/[file].py
      under the correct API version namespace
- [ ] T034 [US2] Integrate with User Story 1 components (if needed)
- [ ] T035 [US2] Implement the required App Router route, middleware,
      or internal API handler in `frontend/src/app/...` when frontend
      is in scope
- [ ] T036 [US2] Extend the selected Design 4 recipe and documented UI
      patterns for the user-facing flow when frontend is in scope

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - [Title] (Priority: P3)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 3 (required) ⚠️

- [ ] T037 [P] [US3] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T038 [P] [US3] Integration test for [user journey] in tests/integration/test_[name].py
- [ ] T039 [P] [US3] Vitest or Playwright coverage for the affected
      frontend flow when frontend is in scope

### Implementation for User Story 3

- [ ] T040 [P] [US3] Create [Entity] model in src/models/[entity].py
- [ ] T041 [US3] Implement [Service] in src/services/[service].py
- [ ] T042 [US3] Implement [endpoint/feature] in src/[location]/[file].py
      under the correct API version namespace
- [ ] T043 [US3] Implement the required App Router route, protected
      server fetch, or Route Handler in `frontend/src/app/...` when
      frontend is in scope
- [ ] T044 [US3] Apply the documented Design 4 visual treatment for the
      user-facing flow when frontend is in scope

**Checkpoint**: All user stories should now be independently functional

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] TXXX [P] Documentation updates in docs/
- [ ] TXXX [P] Publish updated OpenAPI schema and API deprecation notes
- [ ] TXXX Code cleanup and refactoring
- [ ] TXXX Performance optimization across all stories
- [ ] TXXX [P] Additional unit tests in tests/unit/
- [ ] TXXX [P] Frontend loading/error boundary polish and cache
      revalidation review in `frontend/src/app/`
- [ ] TXXX [P] Visual QA against `guide/FRONTEND_DESIGN_SYSTEM.md`,
      `guide/COMPONENT_GUIDE.md`, and `guide/RECIPES.md`
- [ ] TXXX Security hardening
- [ ] TXXX Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for [endpoint] in tests/contract/test_[name].py"
Task: "Integration test for [user journey] in tests/integration/test_[name].py"

# Launch all models for User Story 1 together:
Task: "Create [Entity1] model in src/models/[entity1].py"
Task: "Create [Entity2] model in src/models/[entity2].py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
