<!--
  Sync Impact Report
  ==================
  Version change: N/A → 1.0.0
  Modified principles: N/A (initial ratification)
  Added sections:
    - Core Principles (7 principles)
    - Technology Stack
    - Development Workflow
    - Governance
  Removed sections: None
  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ no changes required
    - .specify/templates/spec-template.md ✅ no changes required
    - .specify/templates/tasks-template.md ✅ no changes required
    - .specify/templates/checklist-template.md ✅ no changes required
    - .specify/templates/agent-file-template.md ✅ no changes required
  Follow-up TODOs: None
-->

# Afrourban Constitution

## Core Principles

### I. HackSoftware Django Styleguide Compliance (NON-NEGOTIABLE)

All Django application code MUST adhere to the
[HackSoftware Django Styleguide](https://github.com/HackSoftware/Django-Styleguide).

- Business logic MUST reside in services and selectors, never in views
  or serializers.
- Models MUST remain thin — no business logic in model methods beyond
  simple property accessors and validation.
- APIs MUST use dedicated input/output serializers; reuse of model
  serializers across boundaries is prohibited.
- Custom exceptions MUST follow the styleguide's error-handling
  patterns.
- All new Django apps MUST follow the prescribed directory layout:
  `services.py`, `selectors.py`, `models.py`, `urls.py`, `views.py`.

**Rationale**: A single authoritative style eliminates architectural
debates and keeps the codebase uniform as the team grows.

### II. API-First Design

Every feature MUST be designed as an API endpoint before any
presentation layer is built, following the
[Microsoft REST API Design Guidelines](https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design).

- Resources MUST be modelled around business entities, not database
  tables.
- Endpoints MUST use standard HTTP methods (GET, POST, PUT, PATCH,
  DELETE) with correct status codes.
- Collection endpoints MUST support filtering, pagination, and sorting.
- API versioning strategy MUST be defined before the first public
  release.
- Error responses MUST use a consistent JSON envelope with `type`,
  `title`, `status`, and `detail` fields (RFC 9457 Problem Details).

**Rationale**: API-first decouples frontend from backend and enables
third-party integrations from day one.

### III. Test-First Development

Tests MUST be written before production code using the Red-Green-Refactor
cycle. Testing MUST be sensible and proportionate — not excessive.

- pytest MUST be the sole test runner. All tests MUST be invoked via
  `poetry run pytest`.
- Every service function and selector MUST have at least one happy-path
  test and one error-path test.
- Integration tests MUST cover API endpoint request/response contracts.
- Unit tests MUST NOT hit the database; use mocks or fakes when
  necessary.
- Factories (e.g., `factory_boy`) MUST be used over hand-crafted
  fixtures.
- Coverage targets SHOULD aim for meaningful coverage of business logic
  rather than arbitrary percentage thresholds.

**Rationale**: Test-first development catches defects early and serves
as living documentation without burdening the team with bureaucratic
coverage mandates.

### IV. Code Quality Enforcement

All code MUST pass automated quality gates before merge.

- **Linting**: Ruff MUST be the sole linter and formatter. Code MUST
  produce zero Ruff warnings under the project's configured rule set.
- **Type Checking**: mypy MUST be run in strict mode on all application
  code. All function signatures MUST include type annotations.
  `type: ignore` comments MUST include an error code and justification.
- Quality checks MUST run in CI and locally via
  `poetry run ruff check .` and `poetry run mypy .`.

**Rationale**: Automated static analysis eliminates entire classes of
bugs and enforces consistency without manual review overhead.

### V. Structured Observability

All runtime output MUST use structured JSON-formatted logging.

- Python's `logging` module MUST be configured with a JSON formatter
  (e.g., `python-json-logger` or `structlog`).
- Every log entry MUST include at minimum: `timestamp`, `level`,
  `logger`, and `message` fields.
- Request-scoped context (e.g., `request_id`, `user_id`) MUST be
  attached to log entries via middleware or context variables.
- Print statements MUST NOT appear in production code.

**Rationale**: Structured logs enable machine parsing, dashboarding, and
alerting — critical for operating a production platform.

### VI. Simplicity & Reuse

Code MUST remain simple, maintainable, and free of unnecessary
abstraction.

- Existing, well-maintained third-party packages MUST be preferred
  over writing new functionality. Before implementing any utility,
  search PyPI for an established solution.
- YAGNI: features or abstractions MUST NOT be added speculatively.
  Every line of code MUST serve a current, concrete requirement.
- Functions MUST be short and single-purpose. If a function exceeds
  ~30 lines, it SHOULD be decomposed.
- Comments MUST explain *why*, not *what*. Self-documenting naming is
  required.

**Rationale**: Simplicity reduces onboarding time, lowers defect rates,
and keeps velocity sustainable.

### VII. Poetry-Managed Toolchain

All Python commands MUST be executed through Poetry.

- Dependencies MUST be managed exclusively via `pyproject.toml` using
  Poetry. Direct `pip install` is prohibited.
- All development commands (tests, linting, type checking, migrations,
  management commands) MUST be run via `poetry run <command>`.
- Lock file (`poetry.lock`) MUST be committed to version control.
- Dependency groups MUST be used to separate dev, test, and production
  dependencies.

**Rationale**: A single dependency manager ensures reproducible
environments across development, CI, and production.

## Technology Stack

| Layer | Technology | Version Constraint |
|-------|-----------|-------------------|
| Language | Python | ^3.11 |
| Framework | Django | 5.1.x |
| Database | PostgreSQL | (via psycopg2-binary) |
| Package Manager | Poetry | latest stable |
| Test Runner | pytest | latest stable |
| Linter/Formatter | Ruff | latest stable |
| Type Checker | mypy | latest stable |
| Logging | structlog or python-json-logger | latest stable |
| WSGI Server (prd) | Gunicorn | latest stable |
| Containerisation | Docker + docker-compose | per compose files |

- New dependencies MUST be evaluated against the simplicity principle
  before adoption: check maintenance status, license compatibility,
  and community traction.
- Framework upgrades MUST be accompanied by a migration plan and full
  test suite pass.

## Development Workflow

### Local Development

1. Clone the repository and run `poetry install`.
2. Copy environment variables from the template and configure
   `afrourban/settings/local.py`.
3. Run migrations: `poetry run python manage.py migrate`.
4. Start the dev server: `poetry run python manage.py runserver` or
   use `docker-compose -f docker-compose.local.yml up`.

### Code Change Lifecycle

1. **Branch**: Create a feature branch from `main`.
2. **Write tests first**: Add failing tests for the new behaviour.
3. **Implement**: Write the minimal code to make tests pass.
4. **Quality gates**: Run `poetry run ruff check .`,
   `poetry run mypy .`, and `poetry run pytest` — all MUST pass.
5. **Review**: Open a pull request; reviewers MUST verify constitution
   compliance.
6. **Merge**: Squash-merge into `main` after approval.

### CI Quality Gates (required to pass before merge)

- `poetry run ruff check .` — zero warnings
- `poetry run mypy .` — zero errors
- `poetry run pytest` — all tests green

## Governance

This constitution is the authoritative source of engineering standards
for the Afrourban project. It supersedes all other conventions,
informal agreements, or ad-hoc practices.

- **Compliance**: Every pull request MUST be reviewed against these
  principles. Violations MUST be resolved before merge.
- **Amendments**: Any change to this constitution MUST be proposed via
  pull request, reviewed by at least one maintainer, and documented
  with a version bump.
- **Versioning**: The constitution follows Semantic Versioning:
  - MAJOR: Principle removed or fundamentally redefined.
  - MINOR: New principle or section added, or material expansion.
  - PATCH: Clarifications, wording fixes, non-semantic refinements.
- **Complexity justification**: Any deviation from these principles
  MUST be documented in the relevant plan's Complexity Tracking table
  with a clear rationale and rejected alternatives.

**Version**: 1.0.0 | **Ratified**: 2026-03-19 | **Last Amended**: 2026-03-19
