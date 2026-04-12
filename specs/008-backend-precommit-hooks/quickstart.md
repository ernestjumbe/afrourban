# Quickstart: Backend Pre-Commit Quality Checks

**Feature**: 008-backend-precommit-hooks  
**Branch**: `008-backend-precommit-hooks`

## Prerequisites

- Python 3.11+
- Poetry installed
- Git available locally
- Repository dependencies installed in a Poetry-managed environment

## Setup

```bash
git checkout 008-backend-precommit-hooks
poetry install
poetry run pre-commit install
poetry run pre-commit run --all-files
```

## Implementation Order

1. Add a failing repository-level pytest module for the pre-commit configuration contract.
2. Add `pre-commit` to the Poetry dev toolchain.
3. Create `.pre-commit-config.yaml` with repository-owned Ruff, mypy, and pytest hooks.
4. Update `README.md` with contributor install, enablement, and verification instructions.
5. Re-run the targeted contract tests and a full `pre-commit` all-files execution.

## Validation Commands

```bash
poetry run pytest tests/test_pre_commit_config.py -q
poetry run pre-commit run --all-files
poetry run ruff check .
poetry run mypy .
poetry run pytest
```

## Validation Checklist

- [X] `poetry run pytest tests/test_pre_commit_config.py -q`
- [X] `poetry run pre-commit run --all-files`
- [X] `poetry run ruff check .`
- [X] `poetry run mypy .`
- [X] `poetry run pytest`

## Latest Validation Results

- `poetry run pytest tests/test_pre_commit_config.py -q` -> `7 passed in 0.04s`
- `poetry run pre-commit run --all-files` -> `backend-ruff`, `backend-mypy`, and `backend-pytest` all passed
- `poetry run ruff check .` -> passed
- `poetry run mypy .` -> `Success: no issues found in 81 source files` with one existing migration note about unchecked untyped function bodies in `users/migrations/0005_backfill_missing_usernames.py`
- `poetry run pytest` -> `119 passed in 1.38s`

## Manual Verification

### 1. Fresh-Clone Setup

- In a fresh local clone, run `poetry install` and `poetry run pre-commit install`.
- Confirm the Git hook installation finishes without requiring repository-specific manual edits.

### 2. All-Files Verification

- Run `poetry run pre-commit run --all-files`.
- Confirm the same three backend hooks run in the documented order.

### 3. Blocking Behavior

- Introduce a backend validation failure and confirm a commit attempt is blocked before completion.

### 4. Retry Path

- Fix the reported failure and rerun `git commit`.
- Confirm the commit can complete normally once all hooks pass.

### 5. Documentation Consistency

- Confirm `README.md` and `.pre-commit-config.yaml` describe the same three backend validation
  categories and the same execution order.

## Expected Output Artifacts

- Root `.pre-commit-config.yaml`
- Updated `pyproject.toml` dev dependencies
- Updated `README.md` contributor workflow guidance
- New `tests/test_pre_commit_config.py`
