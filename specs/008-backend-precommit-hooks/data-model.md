# Data Model: Backend Pre-Commit Quality Checks

**Feature**: 008-backend-precommit-hooks  
**Date**: 2026-03-29

This feature does not introduce database tables. The entities below are conceptual workflow and
contract entities used to define the contributor experience, validation rules, and tests.

## Entity: PreCommitHookDefinition

Represents one required backend validation hook in the repository-owned commit workflow.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `hook_id` | string | required, unique | Stable identifier for the hook in the repository config |
| `validation_category` | enum | required (`style`, `type`, `tests`) | Backend quality gate enforced by the hook |
| `trigger_stage` | enum | required (`commit`) | Local Git workflow stage where the hook runs |
| `execution_scope` | enum | required (`repository`) | Whether the hook validates the full backend repo rather than selected files |
| `blocks_commit_on_failure` | boolean | fixed `true` | Whether a non-zero result prevents commit finalization |
| `display_name` | string | required | Contributor-visible label surfaced on failure |

### Validation Rules

- Exactly three required hook definitions must exist: one each for style validation, type
  validation, and automated tests.
- `hook_id` values must be unique.
- Every hook must block the commit when it fails.
- Every hook must run at the commit stage.

## Entity: HookSetupState

Represents whether a contributor's local clone is ready to enforce the repository commit workflow.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `dependencies_available` | boolean | required | Whether required backend dev dependencies are installed locally |
| `hooks_installed` | boolean | required | Whether the repository hook workflow has been enabled in the clone |
| `verification_completed` | boolean | required | Whether the contributor has confirmed the workflow runs locally |
| `setup_instructions_available` | boolean | fixed `true` | Whether the repository documents install and verification steps |

### Validation Rules

- `verification_completed=true` requires `hooks_installed=true`.
- `hooks_installed=true` requires `dependencies_available=true`.
- Setup instructions must cover both installation and verification.

### State Transitions

```text
not_ready -> installed -> verified
```

- `not_ready -> installed`: occurs after dependencies are available and the contributor enables the
  repository workflow locally.
- `installed -> verified`: occurs after the contributor confirms the hooks run as documented.

## Entity: CommitValidationRun

Represents the outcome of a commit attempt under the configured hook workflow.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `attempt_scope` | enum | required (`backend_changes`) | Type of contributor change being committed |
| `hook_results` | collection | required | Individual outcomes for the required hook definitions |
| `overall_outcome` | enum | required (`passed`, `failed`) | Final commit gating result |
| `failure_category` | enum | optional (`style`, `type`, `tests`) | Validation category that blocked the commit when present |

### Validation Rules

- `overall_outcome=passed` requires all hook results to pass.
- Any failing hook result forces `overall_outcome=failed`.
- When `overall_outcome=failed`, at least one failure category must be identifiable to the
  contributor.

### State Transitions

```text
pending -> passed
pending -> failed
```

- `pending -> passed`: occurs when all required hooks succeed.
- `pending -> failed`: occurs when any required hook fails and the commit is blocked.
