---

description: "Task list for initial frontend application"

---

# Tasks: Initial Frontend Application

**Input**: Design documents from `/specs/011-nextjs-frontend-app/`  
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are REQUIRED by the constitution and by this feature's success criteria; include Vitest, Playwright, type, lint, and build coverage for each user story as applicable.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no unmet dependencies)
- **[Story]**: Which user story this belongs to (`US1`, `US2`, `US3`)
- Every task includes explicit file path targets

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the frontend workspace and repository-level scaffolding needed for implementation.

- [X] T001 Create the frontend workspace manifests in `frontend/package.json`, `frontend/package-lock.json`, `frontend/next.config.ts`, and `frontend/tsconfig.json`
- [X] T002 [P] Create frontend quality-tool configuration files in `frontend/eslint.config.mjs`, `frontend/vitest.config.ts`, and `frontend/playwright.config.ts`
- [X] T003 [P] Create container and environment template files in `frontend/Dockerfile.local` and `frontend/.env.example`
- [X] T004 [P] Create the frontend directory structure under `frontend/src/app/`, `frontend/src/components/`, `frontend/src/lib/`, `frontend/tests/unit/`, `frontend/tests/e2e/`, and `frontend/public/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared runtime, layout, and local-stack infrastructure that all user stories depend on.

**⚠️ CRITICAL**: No user story work should begin until this phase is complete.

- [X] T005 Configure frontend scripts, TypeScript strict mode, and standalone build output in `frontend/package.json`, `frontend/tsconfig.json`, and `frontend/next.config.ts`
- [X] T006 [P] Add shared runtime validation and structured startup logging scaffolding in `frontend/src/lib/env.ts` and `frontend/src/lib/logging.ts`
- [X] T007 [P] Add the base App Router layout, global style entrypoint, and reserved middleware file in `frontend/src/app/layout.tsx`, `frontend/src/app/globals.css`, and `frontend/src/middleware.ts`
- [X] T008 [P] Add shared page shell, launch navigation, and site configuration scaffolding in `frontend/src/components/page-shell.tsx`, `frontend/src/components/site-navigation.tsx`, and `frontend/src/lib/site-config.ts`
- [X] T009 Configure the frontend service, default port mapping, and override support in `docker-compose.local.yml` and `env/.env.docker`

**Checkpoint**: Foundation complete; all user story phases can proceed.

---

## Phase 3: User Story 1 - Team Launches the Public Web App Locally (Priority: P1) 🎯 MVP

**Goal**: Let contributors start the default local stack and reach the public homepage on port `3030`, with documented override support through `4000`.

**Independent Test**: Run `docker compose -f docker-compose.local.yml up --build`, confirm the frontend responds on `http://localhost:3030`, then verify an override such as `FRONTEND_PORT=3031` starts the same homepage on the chosen port.

### Tests for User Story 1 (required) ⚠️

> **NOTE: Write these tests FIRST and confirm they fail before implementation**

- [X] T010 [P] [US1] Add Vitest coverage for default port selection, valid overrides, and invalid override rejection in `frontend/tests/unit/lib/env.test.ts`
- [X] T011 [P] [US1] Add Playwright smoke coverage for homepage availability on the configured base URL in `frontend/tests/e2e/local-startup.spec.ts`

### Implementation for User Story 1

- [X] T012 [P] [US1] Implement runtime config parsing and structured startup failure logging in `frontend/src/lib/env.ts` and `frontend/src/lib/logging.ts`
- [X] T013 [P] [US1] Finalize the frontend container command, healthcheck, and port override handling in `frontend/Dockerfile.local`, `docker-compose.local.yml`, and `env/.env.docker`
- [X] T014 [US1] Document default compose startup, port override flow, and frontend run commands in `README.md` and `frontend/README.md`

**Checkpoint**: Contributors can start and reach the frontend independently of the remaining stories.

---

## Phase 4: User Story 2 - Visitor Sees an Intentional Empty Homepage (Priority: P1) 🎯 MVP

**Goal**: Deliver a public Design 4 homepage with a concise intro, minimal launch navigation, and an intentional empty-state presentation.

**Independent Test**: Open the root route in desktop and mobile viewports, confirm the page uses the editorial shell, shows only available navigation destinations, and presents an intentional empty-state instead of fake listings.

### Tests for User Story 2 (required) ⚠️

- [X] T015 [P] [US2] Add Vitest coverage for the page shell and minimal launch navigation components in `frontend/tests/unit/components/page-shell.test.tsx` and `frontend/tests/unit/components/site-navigation.test.tsx`
- [X] T016 [P] [US2] Add Playwright coverage for homepage empty-state copy and mobile layout behavior in `frontend/tests/e2e/homepage.spec.ts`

### Implementation for User Story 2

- [X] T017 [P] [US2] Implement the homepage intro and intentional empty-state modules in `frontend/src/components/home-hero.tsx` and `frontend/src/components/home-empty-state.tsx`
- [X] T018 [US2] Implement the public root route with shared shell composition and launch-only navigation in `frontend/src/app/page.tsx`, `frontend/src/components/page-shell.tsx`, `frontend/src/components/site-navigation.tsx`, and `frontend/src/lib/site-config.ts`
- [X] T019 [US2] Apply Design 4 tokens, typography, and responsive homepage styling in `frontend/src/app/globals.css`, `frontend/src/components/page-shell.tsx`, `frontend/src/components/home-hero.tsx`, and `frontend/src/components/home-empty-state.tsx`

**Checkpoint**: The public homepage is independently functional and reviewable as the visitor-facing MVP.

---

## Phase 5: User Story 3 - Frontend Contributors Extend the Baseline Safely (Priority: P2)

**Goal**: Make shared versus route-specific ownership obvious, and reserve the right extension points for future BFF and Auth.js work without shipping protected flows now.

**Independent Test**: Inspect the frontend structure and run automated checks to confirm shared shell/navigation primitives remain reusable, homepage-specific content stays scoped to the root route, unavailable destinations are omitted, and reserved middleware/config hooks do not require backend data to render the homepage.

### Tests for User Story 3 (required) ⚠️

- [X] T020 [P] [US3] Add Vitest coverage for launch navigation config and reserved runtime-field behavior in `frontend/tests/unit/lib/site-config.test.ts` and `frontend/tests/unit/lib/env.test.ts`
- [X] T021 [P] [US3] Add Playwright coverage that unavailable destinations are omitted and the homepage remains usable without backend content in `frontend/tests/e2e/homepage.spec.ts`

### Implementation for User Story 3

- [X] T022 [P] [US3] Separate shared primitives from homepage-specific composition in `frontend/src/components/page-shell.tsx`, `frontend/src/components/site-navigation.tsx`, `frontend/src/app/page.tsx`, `frontend/src/components/home-hero.tsx`, and `frontend/src/components/home-empty-state.tsx`
- [X] T023 [P] [US3] Add reserved contributor extension points for future route protection and BFF access in `frontend/src/middleware.ts`, `frontend/src/lib/site-config.ts`, and `frontend/src/lib/env.ts`
- [X] T024 [US3] Document frontend ownership boundaries and future BFF/Auth.js conventions in `frontend/README.md` and `README.md`

**Checkpoint**: Contributors can extend the baseline without guessing where shared shell concerns end and route-local work begins.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finish validation, visual QA, and final documentation consistency across all stories.

- [X] T025 [P] Run visual QA and accessibility refinements against the Design 4 guides in `frontend/src/app/globals.css`, `frontend/src/components/page-shell.tsx`, `frontend/src/components/site-navigation.tsx`, and `frontend/src/components/home-empty-state.tsx`
- [X] T026 Run `docker compose -f docker-compose.local.yml up --build`, `npm run lint`, `npm run typecheck`, `npm run test`, `npm run test:e2e`, and `npm run build`, then record any final validation notes in `specs/011-nextjs-frontend-app/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies; start immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2 and establishes the local-startup MVP path.
- **Phase 4 (US2)**: Depends on Phase 2; recommended after US1 because the homepage relies on the validated runtime and compose wiring from the startup story.
- **Phase 5 (US3)**: Depends on Phase 2; recommended after US2 because it hardens the shared-versus-route-local boundary around the delivered homepage.
- **Phase 6 (Polish)**: Depends on completion of all desired user stories.

### User Story Dependencies

- **US1 (P1)**: Independent after foundational completion.
- **US2 (P1)**: Independent after foundational completion, but smoother after US1 because it relies on the same startup and config surface.
- **US3 (P2)**: Independent after foundational completion, but best completed after US2 so the final route structure and shared primitives already exist.

### Within Each User Story

- Write tests first and confirm they fail before implementation.
- Finish runtime/config plumbing before documentation-only work.
- Finish the route and shared-component implementation before final styling polish.
- Complete each story fully before counting it as shippable.

---

## Parallel Opportunities

- **Setup**: T002, T003, and T004 can run in parallel after T001.
- **Foundational**: T006, T007, and T008 can run in parallel after T005; T009 follows once the frontend workspace exists.
- **US1**: T010 and T011 can run in parallel; T012 and T013 can run in parallel after tests are written.
- **US2**: T015 and T016 can run in parallel; T017 and T019 can run in parallel before T018 assembles the route.
- **US3**: T020 and T021 can run in parallel; T022 and T023 can run in parallel before T024 documents the settled structure.
- **Polish**: T025 can run before the final command bundle in T026.

---

## Parallel Example: User Story 1

```bash
Task: "T010 [US1] runtime config tests in frontend/tests/unit/lib/env.test.ts"
Task: "T011 [US1] local startup smoke test in frontend/tests/e2e/local-startup.spec.ts"
```

## Parallel Example: User Story 2

```bash
Task: "T015 [US2] page shell and navigation tests in frontend/tests/unit/components/page-shell.test.tsx and frontend/tests/unit/components/site-navigation.test.tsx"
Task: "T016 [US2] homepage empty-state Playwright coverage in frontend/tests/e2e/homepage.spec.ts"
```

## Parallel Example: User Story 3

```bash
Task: "T020 [US3] launch navigation config tests in frontend/tests/unit/lib/site-config.test.ts and frontend/tests/unit/lib/env.test.ts"
Task: "T021 [US3] unavailable-destination coverage in frontend/tests/e2e/homepage.spec.ts"
```

---

## Implementation Strategy

### MVP First (User Stories 1 and 2)

1. Complete Phase 1 and Phase 2.
2. Deliver Phase 3 so contributors can start the frontend locally.
3. Deliver Phase 4 so visitors see the intended empty homepage.
4. Validate the compose workflow and public route as the MVP release slice.

### Incremental Delivery

1. Deliver US1 to establish deterministic frontend startup and port handling.
2. Deliver US2 to ship the branded public homepage.
3. Deliver US3 to harden contributor-facing structure and future extension points.
4. Finish with Phase 6 visual QA and full validation.

### Parallel Team Strategy

1. Team completes Setup and Foundational phases together.
2. After foundational completion:
   - Engineer A: US1 runtime/config and compose workflow
   - Engineer B: US2 homepage shell and empty-state UI
   - Engineer C: US3 contributor structure hardening and documentation
3. Coordinate merges carefully for `frontend/src/lib/env.ts`, `frontend/src/components/page-shell.tsx`, and `README.md`.
4. Rejoin for Phase 6 final validation.

---

## Notes

- [P] tasks indicate independently preparable workstreams with different files or clearly separable concerns.
- Every task includes explicit file path targets.
- Suggested MVP scope: **Phase 1 + Phase 2 + Phase 3 + Phase 4 (US1 and US2)**.
- Backend Poetry-managed validation is only required if implementation touches Python-side files.