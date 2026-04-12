# Research: Backend Pre-Commit Quality Checks

**Feature**: 008-backend-precommit-hooks  
**Date**: 2026-03-29

## 1. Pre-Commit Runner Choice

### Decision

Adopt the standard `pre-commit` package as a Poetry-managed dev dependency and own the workflow
through a root `.pre-commit-config.yaml`.

### Rationale

The feature is explicitly about pre-commit hooks, and the `pre-commit` package provides the
expected installation, update, and execution model for local Git hook enforcement. It also keeps
the configuration declarative and repository-owned instead of relying on undocumented per-machine
hook scripts.

### Alternatives considered

- Custom `.git/hooks/pre-commit` script: rejected because it is harder to keep consistent across
  contributors and easier to drift from version-controlled behavior.
- CI-only enforcement: rejected because the requested value is local commit-time feedback before
  code is shared.

## 2. Hook Execution Strategy

### Decision

Define three repository-local hooks that run the existing authoritative Poetry commands for backend
style validation, type validation, and automated tests, in that order. The hooks should operate on
the repository workflow rather than file-by-file subsets.

### Rationale

Ruff, mypy, and pytest are already the repo's source-of-truth quality gates. Reusing those commands
avoids maintaining separate logic for commit hooks. Running style checks before type checks and
tests gives the fastest likely failure feedback and keeps contributor output predictable.

### Alternatives considered

- Use changed-file-only validation for every hook: rejected because mypy and pytest need broader
  project context and changed-file-only behavior would weaken the quality guarantee.
- Use remote Ruff mirrors plus local mypy/pytest hooks: rejected because a single local-hook model
  is simpler and keeps all three checks aligned with the Poetry environment.

## 3. Contributor Documentation Location

### Decision

Publish install, enablement, and verification steps in the repository `README.md` instead of
creating a separate contributor workflow document.

### Rationale

The repo currently has minimal root contributor documentation, so adding the setup path there keeps
the onboarding flow discoverable and avoids scattering one small workflow across extra files.

### Alternatives considered

- Create a dedicated contributor handbook file: rejected because the feature's documentation needs
  are narrow and do not justify an additional documentation surface yet.
- Document setup only in the feature spec artifacts: rejected because contributors need instructions
  in the normal repository docs, not only in planning documents.

## 4. Validation Strategy

### Decision

Use a repository-level pytest module to verify the committed pre-commit configuration and documented
workflow contract, then validate the operational behavior with `poetry run pre-commit run
--all-files`.

### Rationale

This satisfies the constitution's test-first requirement for a non-runtime feature and gives the
team regression protection if the hook definitions or documentation drift later.

### Alternatives considered

- Manual verification only: rejected because configuration drift would be easy to reintroduce.
- No pytest coverage because the feature is tooling-only: rejected because the constitution still
  requires planned tests before implementation.
