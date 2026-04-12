# afrourban

## Backend Pre-Commit Workflow

Use the repository-owned pre-commit workflow in every local clone so the same backend quality gates
run before `git commit` succeeds.

### Install

```bash
poetry install
poetry run pre-commit install
```

### Verify

```bash
poetry run pre-commit run --all-files
```

### Commit-Time Gates

Every contributor runs the same three backend quality gates, in this order, before a commit is
accepted:

- `backend-ruff`
- `backend-mypy`
- `backend-pytest`

The hooks validate repository-wide backend state rather than silently reducing checks to only the
currently staged filenames.

### Retry After Failure

If a hook fails during a commit, fix the reported issue and retry the same commit flow. After
fixing the failure, run `git commit` again.
