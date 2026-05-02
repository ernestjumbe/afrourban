# Research: Initial Frontend Application

## Decision 1: Build the first public web surface as a dedicated `frontend/` Next.js App Router application

- **Decision**: Create a new top-level `frontend/` application using the Next.js App Router, TypeScript, and a standalone production build target.
- **Rationale**: The constitution requires `frontend/src/app`, React Server Components by default, and a BFF-first model for all future backend access. A dedicated Next.js app cleanly separates the Node toolchain from the Django backend while still allowing Docker Compose orchestration at the repository root.
- **Alternatives considered**:
  - Django templates: rejected because they do not satisfy the App Router and BFF requirements.
  - Vite or another SPA framework: rejected because they would add a separate client-side data access model that conflicts with the server-first BFF rule.
  - Embedding the frontend inside the Django tree: rejected because it would blur Python and Node toolchains and make standalone frontend builds harder to reason about.

## Decision 2: Keep the bootstrap homepage static and server-rendered, with no live backend data dependency

- **Decision**: Deliver the homepage as a server-rendered public route that uses only static copy, shared design tokens, and reusable shell/navigation components.
- **Rationale**: The spec explicitly requires the empty homepage to remain usable while backend content services are unavailable. Keeping the first slice static reduces risk, speeds local startup, and avoids introducing premature Route Handlers or proxy code.
- **Alternatives considered**:
  - Fetching placeholder content from Django: rejected because it would create an unnecessary dependency on backend availability.
  - Mock data grids or fake listings: rejected because the spec forbids misleading filler content.
  - Client-side hydration for the full homepage: rejected because the feature benefits from default Server Components and minimal runtime JavaScript.

## Decision 3: Expose the frontend as part of the default local Docker Compose stack on port `3030`, with overrides through `4000`

- **Decision**: Add a dedicated `frontend` service to `docker-compose.local.yml`, include it in the default startup path, map `3030:3030` by default, and support overrides through a `FRONTEND_PORT` environment variable constrained to the `3030-4000` range.
- **Rationale**: The spec clarifications require the frontend to be available on its own port, default to `3030`, and start as part of the shared local workflow. A dedicated service preserves isolation while keeping onboarding and smoke testing simple.
- **Alternatives considered**:
  - Proxying the frontend through Django: rejected because it adds unnecessary coupling to the backend web stack.
  - Automatic first-free-port discovery: rejected because deterministic ports are better for documentation and automated validation.
  - Optional compose profile: rejected because the clarified requirement is to include the frontend in the default startup path.

## Decision 4: Implement the Design 4 homepage with shared shell primitives and a minimal launch navigation

- **Decision**: Reuse the documented Page Shell and Navigation patterns, apply the Editorial Index recipe as the closest page composition, and replace its featured/grid content zones with a single intentional empty-state module.
- **Rationale**: The guides require the closest documented recipe and component patterns to be reused before inventing new layout language. The homepage needs a deliberate editorial frame without implying content exists where none has been published yet.
- **Alternatives considered**:
  - Full editorial card grid with empty placeholders: rejected because it visually suggests unavailable content.
  - Pure hero-only landing page: rejected because it would underuse the documented shell/navigation vocabulary needed for future routes.
  - Disabled placeholder navigation items: rejected because the user clarified that only currently available destinations should be clickable.

## Decision 5: Validate runtime configuration with Zod before boot and reserve Auth.js integration for the first protected route

- **Decision**: Introduce a server-only runtime configuration module that validates required environment variables with Zod. Reserve Auth.js v5 scaffolding through directory structure and environment planning, but do not implement login flows or protected routes in this feature.
- **Rationale**: The constitution requires Zod validation for environment inputs and Auth.js v5 for future protected routes. The delivered homepage is fully public, so shipping auth dependencies and flows now would add dead weight without user value.
- **Alternatives considered**:
  - Postponing environment validation: rejected because the spec requires fast failure for missing runtime config.
  - Fully wiring Auth.js during bootstrap: rejected because no protected routes or credentials flow are in scope.
  - Leaving no auth reservation at all: rejected because future routes need a clear place to attach middleware and server-side session handling.

## Decision 6: Treat frontend validation as five gates: lint, type, unit, e2e, and standalone build

- **Decision**: The bootstrap feature will define validation around ESLint `next/core-web-vitals`, TypeScript strict mode, Vitest, Playwright, and `next build` with standalone output.
- **Rationale**: These five checks align directly with the frontend quality requirements in the constitution and are sufficient to prove that the empty homepage renders correctly, responds on mobile, and remains production-buildable.
- **Alternatives considered**:
  - E2E-only validation: rejected because configuration and component regressions should fail earlier than browser automation.
  - Lint/type only: rejected because it would not prove route behavior or responsive empty-state rendering.
  - Deferring standalone build verification: rejected because container deployment is part of the feature’s scope.

## Decision 7: Define minimal structured logging now without building speculative BFF runtime code

- **Decision**: Add a small server-side logging utility for JSON-formatted startup and runtime configuration failures, and reserve request-context propagation through middleware-safe utilities for future authenticated or data-backed routes.
- **Rationale**: The constitution requires structured observability, but this feature does not yet have backend fetches, route handlers, or user sessions. A minimal server-side strategy satisfies the governance requirement without inventing unused infrastructure.
- **Alternatives considered**:
  - No frontend logging strategy yet: rejected because it leaves the observability gate unresolved.
  - Full request-id propagation and audit logging now: rejected because the homepage has no meaningful BFF traffic to instrument yet.
  - Browser console instrumentation: rejected because it does not meet the structured server-side logging requirement.