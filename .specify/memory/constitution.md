<!--
  Sync Impact Report
  ==================
  Version change: 1.2.0 → 1.3.0
  Modified principles:
    - IX. UI Styling & Design System Fidelity (new principle)
  Added sections:
    - IX. UI Styling & Design System Fidelity (NON-NEGOTIABLE)
  Removed sections: None
  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ updated
    - .specify/templates/spec-template.md ✅ updated
    - .specify/templates/tasks-template.md ✅ updated
    - .specify/templates/commands/*.md ⚠ directory not present (no action taken)
    - AGENTS.md ✅ updated
    - .github/agents/copilot-instructions.md ✅ updated
    - README.md ✅ no changes required
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
- API documentation MUST be generated and maintained with
  `drf-spectacular`, and the published schema MUST use OpenAPI 3.0+.
- APIs MUST be explicitly versioned with URL namespaces such as
  `/api/v1/`, `/api/v2/`, and so on.
- All API URL routes MUST be registered in an `api_urlpatterns` list in
  the main `urls.py`, then included under the `/api/` namespace.
- Breaking API changes MUST be introduced in a new version namespace
  rather than replacing existing versioned endpoints in place.
- Deprecated API versions MUST include a documented deprecation policy
  with deprecation date, planned removal date, and migration path.
- Error responses MUST use a consistent JSON envelope with `type`,
  `title`, `status`, and `detail` fields (RFC 9457 Problem Details).

**Rationale**: API-first decouples frontend from backend and enables
third-party integrations from day one while keeping contracts explicit
and safely evolvable over time.

### III. Test-First Development

Tests MUST be written before production code using the Red-Green-Refactor
cycle. Testing MUST be sensible and proportionate — not excessive.

- Backend tests MUST use pytest and be invoked via `poetry run pytest`.
- Frontend unit and component tests MUST use Vitest.
- Frontend end-to-end tests MUST use Playwright for route protection,
  authentication journeys, and critical BFF flows.
- Every backend service function and selector MUST have at least one
  happy-path test and one error-path test.
- Frontend route segments, server actions, route handlers, and shared
  validation schemas MUST each have behavior-focused tests at the most
  appropriate layer.
- Integration tests MUST cover API endpoint request/response contracts.
- Unit tests MUST NOT hit the database or external APIs; use mocks,
  fakes, or contract fixtures when necessary.
- Factories (e.g., `factory_boy`) MUST be used over hand-crafted
  backend fixtures.
- Coverage targets SHOULD aim for meaningful coverage of business logic
  and user-critical frontend paths rather than arbitrary percentage
  thresholds.

**Rationale**: Test-first development catches defects early and serves
as living documentation without burdening the team with bureaucratic
coverage mandates.

### IV. Code Quality Enforcement

All code MUST pass automated quality gates before merge.

- **Backend linting**: Ruff MUST be the sole Python linter and
  formatter. Backend code MUST produce zero Ruff warnings under the
  project's configured rule set.
- **Backend typing**: mypy MUST be run in strict mode on Python
  application code. All function signatures MUST include type
  annotations. `type: ignore` comments MUST include an error code and
  justification.
- **Frontend typing**: TypeScript strict mode MUST be enabled for all
  frontend code. Unsafe casts, `any`, and unchecked external payloads
  MUST be isolated behind explicit Zod parsing boundaries.
- **Frontend linting**: ESLint MUST enforce the `next/core-web-vitals`
  configuration for the frontend.
- **Validation**: Zod MUST be used for frontend environment variables,
  form inputs, and external API response validation.
- Quality checks MUST run in CI and locally. Backend checks MUST use
  `poetry run ruff check .` and `poetry run mypy .`. Frontend checks
  MUST include lint, typecheck, Vitest, Playwright coverage for changed
  flows, and a production `next build`.

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

### VIII. Frontend Server-First BFF Architecture (NON-NEGOTIABLE)

All frontend work MUST follow modern Next.js App Router practices and
use the Next.js server as the Backend-for-Frontend for the Django API.

- The frontend MUST use the App Router exclusively under
  `frontend/src/app`. The Pages Router is forbidden.
- Route segments MUST colocate their components, logic, and route-local
  types. Shared UI MUST live under `frontend/src/components`, shared
  utilities under `frontend/src/lib`, shared hooks under
  `frontend/src/hooks`, shared types under `frontend/src/types`, and
  route protection in `frontend/src/middleware.ts`.
- React Server Components MUST be the default. `'use client'` MAY be
  added only for browser APIs, event handlers, or React client hooks.
- The Next.js server MUST broker external API access. Client code MUST
  NOT call the Django REST API directly. Mutations MUST use Server
  Actions. Client-side data fetching MUST use internal Route Handlers
  under `frontend/src/app/api/` when a browser request is required.
- Server Components MUST fetch data with native `fetch`, use Next.js
  caching and revalidation intentionally, and provide explicit loading
  and error boundaries.
- Sensitive credentials, API keys, refresh tokens, and server-only URLs
  MUST NEVER be exposed to the client bundle.
- Authentication MUST use Auth.js v5 with the Credentials provider
  against the Django `/api/v1/auth/login/` endpoint.
- Django-issued access and refresh tokens MUST be stored in the
  encrypted Auth.js session token via callbacks. Token refresh MUST be
  implemented in the Auth.js `jwt` callback using
  `/api/v1/auth/refresh/`, and expired refresh tokens MUST force
  re-authentication.
- Protected frontend routes MUST use Auth.js middleware and redirect
  unauthenticated users to login.
- Server Components and Route Handlers calling external APIs MUST load
  the user session via `auth()`, attach
  `Authorization: Bearer <accessToken>`, and fail closed when the
  session is absent or invalid.
- Frontend deployments MUST validate required environment variables at
  build time with Zod, including `AUTH_SECRET`, `AUTH_TRUST_HOST`,
  `API_URL`, and any `NEXT_PUBLIC_*` values intentionally exposed.
- The frontend build output for container deployment MUST set
  `output: 'standalone'` in `next.config.js`.

**Rationale**: A server-first BFF keeps authentication, authorization,
and API contracts on the trusted server boundary while aligning the
frontend with current Next.js operational and performance best
practices.

### IX. UI Styling & Design System Fidelity (NON-NEGOTIABLE)

All frontend UI work MUST follow the AfroUrban Design 4 system and the
guide documents that define page shells, components, and page recipes.

- Frontend styling decisions MUST follow `guide/FRONTEND_DESIGN_SYSTEM.md`,
  `guide/COMPONENT_GUIDE.md`, and `guide/RECIPES.md` before inventing
  new patterns.
- The default visual direction MUST remain dark-first editorial,
  combining Scandinavian restraint with African geometric identity.
  Light mode MAY be supported, but it MUST preserve the same hierarchy,
  spacing, and component structure.
- Major narrative headings MUST use serif typography. Navigation,
  labels, chips, and interface controls MUST use uppercase tracked sans.
  Body copy MUST remain readable, calm, and appropriately narrow for
  long-form content.
- Gold MUST remain the primary action accent. Terracotta MUST remain
  the category and editorial accent. Bright blue SaaS-style accents,
  neon gradients, heavy shadows, and generic dashboard aesthetics are
  prohibited.
- Full-page views MUST use the Design 4 page shell vocabulary where it
  fits the page type: gold trim, sticky translucent navigation,
  restrained background patterning, generous spacing, and large-radius
  surfaces.
- Page composition MUST follow the closest approved recipe before a new
  layout is introduced. Indexes MUST stay editorial, directory pages
  MUST avoid dashboard density, auth pages MUST keep calm branded
  shells, detail pages MUST let imagery lead, and feature landings MUST
  vary module scale intentionally.
- Components MUST reuse the closest documented pattern before creating
  new component language. New variants MUST stay within the Design 4
  vocabulary for shape, spacing, motion, and emphasis.
- Patterns and ornament MAY appear in heroes, trims, or low-contrast
  background fields, but MUST NOT sit behind readable body copy.
- Motion MUST stay understated: short fades, slide-ins, and small
  translate shifts only. Bounce, overshoot, and playful motion are
  prohibited.
- Mobile layouts MUST feel composed rather than merely stacked. Search,
  filters, and navigation MUST stay accessible without overwhelming the
  editorial tone.
- Frontend reviews MUST verify that the implemented page cites the
  closest matching recipe or documented component pattern whenever a
  full page or shared component is introduced.

**Rationale**: A single visual system preserves AfroUrban's editorial
identity across features and keeps product work from drifting into
generic web UI patterns.

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
| API Schema | drf-spectacular | OpenAPI 3.0+ |
| Logging | structlog or python-json-logger | latest stable |
| Frontend Framework | Next.js | App Router-only current stable |
| Frontend Auth | Auth.js | v5 |
| Frontend Validation | Zod | latest stable |
| Frontend Unit/Component Testing | Vitest | latest stable |
| Frontend E2E Testing | Playwright | latest stable |
| Frontend Design System | AfroUrban Design 4 guides | current repo version |
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
2. When a frontend workspace is present, install frontend dependencies
  with the frontend package manager and commit the lock file.
3. Copy environment variables from the template and configure backend
  and frontend settings, including the Auth.js and API URL variables
  required by the frontend.
4. Run migrations: `poetry run python manage.py migrate`.
5. Start the backend dev server with `poetry run python manage.py
  runserver` or use `docker-compose -f docker-compose.local.yml up`.
6. When frontend work is in scope, run the Next.js dev server from the
  frontend workspace and verify middleware-protected routes locally.

### Code Change Lifecycle

1. **Branch**: Create a feature branch from `main`.
2. **Write tests first**: Add failing tests for the new behaviour.
3. **Implement**: Write the minimal code to make tests pass.
4. **Quality gates**: Run `poetry run ruff check .`,
  `poetry run mypy .`, and `poetry run pytest` for backend changes.
  Frontend changes MUST also pass lint, TypeScript strict typecheck,
  Vitest, the relevant Playwright coverage, and `next build`. For API
  contract changes, `poetry run python manage.py spectacular --file
  schema.yaml --validate` MUST also pass.
5. **Review**: Open a pull request; reviewers MUST verify constitution
   compliance.
6. **Merge**: Squash-merge into `main` after approval.

### CI Quality Gates (required to pass before merge)

- `poetry run ruff check .` — zero warnings
- `poetry run mypy .` — zero errors
- `poetry run pytest` — all tests green
- Frontend lint, TypeScript strict typecheck, Vitest, Playwright, and
  `next build` — required when frontend code changes; all MUST pass
- `poetry run python manage.py spectacular --file schema.yaml --validate`
  — required for API changes; schema validation MUST pass

## Governance

This constitution is the authoritative source of engineering standards
for the Afrourban project. It supersedes all other conventions,
informal agreements, or ad-hoc practices.

- **Compliance**: Every pull request MUST be reviewed against these
  principles. Violations MUST be resolved before merge.
- **API compliance evidence**: Pull requests that add or modify APIs
  MUST show `drf-spectacular` schema updates, versioned path compliance,
  `api_urlpatterns` registration in main `urls.py`, and deprecation
  policy updates when applicable.
- **Frontend compliance evidence**: Pull requests that add or modify
  frontend code MUST show App Router placement, server/client boundary
  justification, Auth.js v5 token handling, Zod validation coverage,
  Vitest/Playwright evidence for the affected flows, and the Design 4
  recipe or component pattern that the UI follows.
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

**Version**: 1.3.0 | **Ratified**: 2026-03-19 | **Last Amended**: 2026-05-02
