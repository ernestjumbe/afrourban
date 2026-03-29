# Pre-Commit Workflow Contract

**Feature**: 008-backend-precommit-hooks  
**Date**: 2026-03-29

## 1. Workflow Scope

1. The repository MUST provide a pre-commit workflow for backend contributor commits.
2. The workflow applies to local contributor commit attempts and does not change deployed runtime
   behavior or public API behavior.
3. The workflow MUST cover exactly these backend validation categories:
   - style validation
   - type validation
   - automated tests

## 2. Hook Registration Contract

1. A committed root `.pre-commit-config.yaml` file MUST define the repository-owned hook workflow.
2. The configuration MUST declare three required hooks with stable IDs:
   - `backend-ruff`
   - `backend-mypy`
   - `backend-pytest`
3. Each hook MUST execute through Poetry and use the repository's authoritative validation command
   for its category.
4. Each hook MUST run during the pre-commit stage and MUST block commit finalization on failure.
5. The hooks MUST execute in a stable contributor-facing order: style validation, then type
   validation, then automated tests.
6. The workflow MUST validate repository state rather than silently reducing checks to a smaller
   changed-file subset for categories that need broader project context.

## 3. Contributor Setup Contract

1. The repository MUST document how contributors install the required development dependencies.
2. The repository MUST document how contributors enable the local pre-commit workflow after
   installing dependencies.
3. The repository MUST document how contributors verify that the workflow is active in a fresh
   clone.
4. The install, enablement, and verification instructions MUST be available in normal repository
   contributor documentation.

## 4. Success And Failure Semantics

1. If any required hook fails, the commit MUST be rejected before it is finalized.
2. Failure output MUST make the failing validation category identifiable to the contributor.
3. If all required hooks pass, the commit MUST be allowed to complete without an alternate manual
   approval step.
4. After correcting a failure, contributors MUST be able to retry the same commit workflow without
   a separate recovery path.

## 5. Validation Contract

1. Repository-level automated tests MUST verify that the committed pre-commit configuration defines
   the required hook categories.
2. Repository-level automated tests MUST verify that contributor documentation covers install and
   verification steps.
3. Final feature validation MUST include an all-files pre-commit run in addition to the standard
   Ruff, mypy, and pytest quality gates.
