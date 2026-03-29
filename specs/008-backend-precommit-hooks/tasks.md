---

description: "Task list for backend pre-commit quality checks"
---

# Tasks: Backend Pre-Commit Quality Checks

**Input**: Design documents from `/specs/008-backend-precommit-hooks/`  
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED by the constitution and by this feature's success criteria; include repository-level contract coverage and workflow validation for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no unmet dependencies)
- **[Story]**: Which user story this belongs to (`US1`, `US2`, `US3`)
- Every task includes explicit file path targets

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the repository-level scaffolding for tooling config, contributor docs, and validation tests.

- [X] T001 Create the repository-level tooling test scaffold in `tests/__init__.py` and `tests/test_pre_commit_config.py`
- [X] T002 [P] Create the root pre-commit workflow scaffold in `.pre-commit-config.yaml`
- [X] T003 [P] Add a backend contributor workflow placeholder section in `README.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared toolchain dependency required by every user story.

**⚠️ CRITICAL**: No user story work should begin until this phase is complete.

- [X] T004 Add `pre-commit` to `[tool.poetry.group.dev.dependencies]` in `pyproject.toml`

**Checkpoint**: Foundation complete; the repository can install and execute the planned commit-time workflow.

---

## Phase 3: User Story 1 - Block Broken Backend Commits Early (Priority: P1) 🎯 MVP

**Goal**: Ensure backend commits are blocked locally whenever Ruff, mypy, or backend tests fail.

**Independent Test**: Introduce a backend validation failure, attempt a commit, and verify that the configured pre-commit workflow blocks the commit and identifies the failing validation category.

### Tests for User Story 1 (required) ⚠️

> **NOTE: Write these tests FIRST and confirm they fail before implementation**

- [X] T005 [US1] Add failing contract tests for required hook IDs, commit-stage registration, and Poetry-backed validation commands in `tests/test_pre_commit_config.py`

### Implementation for User Story 1

- [X] T006 [US1] Implement `backend-ruff`, `backend-mypy`, and `backend-pytest` hook definitions in `.pre-commit-config.yaml`
- [X] T007 [US1] Configure the three hooks for repository-scoped Ruff, mypy, and pytest execution via Poetry in `.pre-commit-config.yaml`

**Checkpoint**: User Story 1 is independently functional and can serve as the MVP release.

---

## Phase 4: User Story 2 - Enable the Hooks Reliably in Local Clones (Priority: P2)

**Goal**: Give contributors clear setup and verification steps so the pre-commit workflow can be enabled consistently in fresh clones.

**Independent Test**: Follow the documented repository setup steps in a fresh clone and verify that the local pre-commit workflow is installed and can be triggered successfully.

### Tests for User Story 2 (required) ⚠️

- [X] T008 [US2] Add failing documentation contract tests for install, enablement, and verification instructions in `tests/test_pre_commit_config.py`

### Implementation for User Story 2

- [X] T009 [US2] Document contributor setup and `pre-commit install` steps in `README.md`
- [X] T010 [US2] Document local verification and retry guidance for the pre-commit workflow in `README.md`

**Checkpoint**: User Story 2 is independently testable through fresh-clone setup and verification flow coverage.

---

## Phase 5: User Story 3 - Keep the Workflow Predictable for the Team (Priority: P3)

**Goal**: Constrain the workflow to the agreed three backend validation categories and document the same stable expectations for all contributors.

**Independent Test**: Review the committed hook configuration and contributor guidance, then verify that the workflow always exposes the same three backend validation categories in the same order.

### Tests for User Story 3 (required) ⚠️

- [X] T011 [US3] Add failing tests for stable hook order, three-category scope, and repository-wide validation semantics in `tests/test_pre_commit_config.py`

### Implementation for User Story 3

- [X] T012 [US3] Refine `.pre-commit-config.yaml` to preserve stable hook order and limit the workflow to the agreed backend validation categories
- [X] T013 [US3] Update `README.md` to describe the shared three-hook workflow and consistent contributor expectations

**Checkpoint**: User Story 3 is independently verifiable through workflow-scope and consistency checks.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize release-facing guidance and run full workflow validation across all stories.

- [X] T014 [P] Normalize the final contributor workflow wording and command snippets in `README.md`
- [X] T015 [P] Refresh the validation checklist and manual verification flow in `specs/008-backend-precommit-hooks/quickstart.md`
- [X] T016 Run `poetry run pytest tests/test_pre_commit_config.py -q` and `poetry run pre-commit run --all-files`, then record outcomes in `specs/008-backend-precommit-hooks/quickstart.md`
- [X] T017 Run `poetry run ruff check .`, `poetry run mypy .`, and `poetry run pytest`, then record outcomes in `specs/008-backend-precommit-hooks/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies; start immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2 and defines the MVP cut line.
- **Phase 4 (US2)**: Depends on Phase 2; safest after US1 because the docs must describe the live hook workflow accurately.
- **Phase 5 (US3)**: Depends on Phase 2; safest after US1 because it tightens the same hook configuration and contributor guidance.
- **Phase 6 (Polish)**: Depends on completion of all desired user stories.

### User Story Dependencies

- **US1 (P1)**: Independent after foundational completion.
- **US2 (P2)**: Depends on the existence of the US1 workflow so setup and verification docs describe the real committed hook behavior.
- **US3 (P3)**: Depends on the US1 workflow and then constrains its long-term scope and consistency expectations.

### Within Each User Story

- Tests MUST be written and fail before implementation.
- Hook configuration before contributor-facing documentation that describes it.
- Core workflow behavior before final validation and release notes.
- Finish each story completely before treating it as shippable.

### Parallel Opportunities

- **Setup**: T002 and T003 can run in parallel after T001.
- **Polish**: T014 and T015 can run in parallel before T016.

---

## Parallel Example: Setup

```bash
Task: "T002 Create the root pre-commit workflow scaffold in .pre-commit-config.yaml"
Task: "T003 Add a backend contributor workflow placeholder section in README.md"
```

## Parallel Example: Polish

```bash
Task: "T014 Normalize the final contributor workflow wording and command snippets in README.md"
Task: "T015 Refresh the validation checklist and manual verification flow in specs/008-backend-precommit-hooks/quickstart.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Deliver Phase 3 (US1).
3. Validate the local pre-commit workflow blocks failing backend changes.
4. Demo or release the core workflow if needed.

### Incremental Delivery

1. Deliver US1 to establish the core commit-blocking workflow.
2. Deliver US2 to make setup and verification reliable in fresh clones.
3. Deliver US3 to lock in the shared workflow scope and contributor expectations.
4. Finish with Phase 6 documentation cleanup and full validation.

### Parallel Team Strategy

1. Team completes Setup and Foundational phases together.
2. After foundational completion:
   - Engineer A: US1 hook configuration and blocking behavior
   - Engineer B: US2 setup and verification documentation
   - Engineer C: US3 workflow consistency and scope refinement
3. Rejoin for Phase 6 final documentation normalization and validation.

---

## Notes

- [P] tasks indicate different files or independently preparable workstreams.
- Every task includes explicit file path targets.
- Suggested MVP scope: **Phase 1 + Phase 2 + Phase 3 (US1)**.
- Execute all validation commands with `poetry run` per constitution.
