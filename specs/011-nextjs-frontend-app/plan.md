# Implementation Plan: Initial Frontend Application

**Branch**: `011-nextjs-frontend-app` | **Date**: 2026-05-02 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/011-nextjs-frontend-app/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add the repository's first dedicated `frontend/` application as a Next.js App Router web app,
wire it into the default local Docker Compose startup path on port `3030` with override support
through `4000`, and ship a public editorial homepage that reuses the AfroUrban Design 4 page shell
and navigation patterns while presenting an intentional empty launch state without any live backend
data dependency.

## Technical Context

**Language/Version**: Python 3.11 for the existing backend; Node.js 20 LTS + TypeScript 5.x for the new frontend  
**Primary Dependencies**: Next.js App Router, React 19, Zod, ESLint `next/core-web-vitals`, Vitest, Playwright, existing Docker Compose stack; Auth.js v5 reserved for future protected routes  
**Storage**: N/A for the delivered homepage; file-based frontend source, static assets, and environment configuration only  
**Testing**: Vitest for component/config behavior, Playwright for homepage and responsive smoke coverage, TypeScript strict checks, ESLint, and `next build` standalone validation; backend Poetry checks remain available if any Python files change  
**Target Platform**: Local macOS development via Docker Compose; Linux container deployment target for the frontend service  
**Project Type**: Web application with a Next.js frontend and existing Django API backend  
**Performance Goals**: Homepage renders without backend fetches, route output stays within a single server render pass, local startup exposes a healthy page on port `3030` by default, and production `next build` succeeds with standalone output  
**Constraints**: Use `frontend/src/app` only, keep React Server Components as the default, do not call the Django API from browser code, include the frontend in default local compose startup, keep the homepage public, validate runtime env before boot, preserve Design 4 editorial styling, and support a `3030-4000` local port override range  
**Scale/Scope**: One new top-level frontend app, one public root route, shared shell/navigation primitives, runtime config validation, local Docker service wiring, frontend test/build scaffolding, and onboarding documentation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. HackSoftware Styleguide | PASS | No new backend business logic is introduced; any supporting backend/config edits stay thin and do not violate services/selectors boundaries |
| II. API-First Design | PASS | Feature adds no Django API endpoints; API contract impact is explicitly N/A and future backend access remains reserved for BFF-only server boundaries |
| II.a Deprecation Policy | PASS | No deprecated endpoint or API version is introduced |
| III. Test-First Development | PASS | Plan starts with failing frontend lint/type/unit/e2e checks for the homepage shell, runtime config, and compose startup expectations |
| IV. Code Quality | PASS | Validation plan includes frontend ESLint, TypeScript strict mode, Vitest, Playwright, and standalone build; backend Ruff/mypy/pytest remain available if Python support files are touched |
| V. Structured Observability | PASS | Design defines server-side structured JSON logging for startup/config validation failures and a request-context strategy reserved in middleware-safe utilities for future BFF routes |
| VI. Simplicity & Reuse | PASS | A single `frontend/` app is added, the homepage stays static, no speculative Route Handlers are introduced, and design reuses documented Page Shell and Navigation patterns |
| VII. Poetry-Managed Toolchain | PASS | All Python-side commands remain `poetry run ...`; Node-side validation is isolated to frontend package scripts without changing backend dependency management |
| VIII. Frontend Server-First BFF Architecture | PASS | App Router is used exclusively under `frontend/src/app`, browser-side API access is forbidden, homepage ships as a Server Component path, and future auth remains explicitly reserved for Auth.js v5 |
| IX. UI Styling & Design System Fidelity | PASS | Plan uses the Editorial Index recipe with an intentional empty-state substitution and reuses the documented Page Shell and Navigation patterns |

**Pre-Phase 0 gate: PASS** — no constitution violations.

## Phase 0 Research Summary

Research decisions are captured in [research.md](research.md), covering:

1. Why the first frontend should be a dedicated top-level `frontend/` Next.js App Router app rather than a Vite app, Django-templated page, or proxied subpath
2. Why the bootstrap should favor a static public homepage, server-only runtime config validation, and no live BFF routes in the first slice
3. How the default Docker Compose startup path should expose the frontend on port `3030` with an override range through `4000`
4. How the homepage should reuse the Editorial Index recipe, Page Shell, and Navigation patterns while intentionally omitting unavailable destinations
5. Why frontend quality gates should start with lint, type, unit, e2e, and standalone build coverage for this bootstrap feature
6. How the frontend should define minimal structured logging now without overbuilding BFF behavior before the first data-backed route exists

## Project Structure

### Documentation (this feature)

```text
specs/011-nextjs-frontend-app/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── public-web-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
docker-compose.local.yml                 # add the frontend service to the default local stack
env/
└── .env.docker                          # define FRONTEND_PORT and shared compose env

frontend/
├── Dockerfile.local                     # local development image for Next.js
├── package.json
├── package-lock.json
├── next.config.ts                       # standalone output
├── tsconfig.json                        # strict mode
├── eslint.config.mjs
├── vitest.config.ts
├── playwright.config.ts
├── .env.example
├── public/
│   └── ...
├── src/
│   ├── app/
│   │   ├── layout.tsx                   # shared document shell
│   │   ├── page.tsx                     # homepage route
│   │   └── globals.css                  # design tokens and global styles
│   ├── components/
│   │   ├── page-shell.tsx               # reusable Design 4 frame
│   │   ├── site-navigation.tsx          # minimal launch navigation
│   │   ├── home-hero.tsx                # homepage intro
│   │   └── home-empty-state.tsx         # intentional empty-state module
│   ├── lib/
│   │   ├── env.ts                       # Zod runtime validation
│   │   ├── logging.ts                   # structured server-side logging helper
│   │   └── site-config.ts               # navigation and copy config
│   └── middleware.ts                    # reserved route protection/request-context entry point
└── tests/
    ├── unit/
    │   ├── components/
    │   └── lib/
    └── e2e/
        └── homepage.spec.ts

README.md                                # document frontend startup path and local URLs
Makefile                                 # optional frontend helper targets if adopted during implementation
```

**Structure Decision**: Implement the feature as a new top-level `frontend/` web application so the
Node toolchain, App Router routes, and browser-facing build artifacts stay isolated from the Django
backend while still participating in the repository’s default Docker Compose workflow.

## Phase 1 Design Artifacts

- [data-model.md](data-model.md): Defines the runtime configuration, shell/navigation, and empty-state view models that control the bootstrap homepage.
- [contracts/public-web-contract.md](contracts/public-web-contract.md): Defines the public route, navigation, and runtime configuration contract for the initial web app.
- [quickstart.md](quickstart.md): Provides the ordered implementation and validation workflow, including Docker Compose startup, frontend quality gates, and port override handling.

## Constitution Check (Post-Design Re-check)

| Principle | Status | Notes |
|-----------|--------|-------|
| I. HackSoftware Styleguide | PASS | Design stays frontend-focused and does not introduce backend business logic shortcuts |
| II. API-First Design | PASS | Contract explicitly documents that no Django API surface changes land in this slice and that future backend access must remain server-brokered |
| II.a Deprecation Policy | PASS | No deprecated route or version is introduced |
| III. Test-First Development | PASS | Quickstart begins with failing homepage behavior, navigation, runtime-config, and Docker-startup checks before implementation |
| IV. Code Quality | PASS | Design requires ESLint, TypeScript strict mode, Vitest, Playwright, and standalone build verification, with backend Poetry checks retained if supporting backend files change |
| V. Structured Observability | PASS | Structured server logging is defined for env validation, container boot failures, and future request context propagation through middleware-safe utilities |
| VI. Simplicity & Reuse | PASS | Design uses one route, one shell, one empty-state module, and the closest documented design patterns without speculative data plumbing |
| VII. Poetry-Managed Toolchain | PASS | Backend commands remain Poetry-managed; frontend commands stay encapsulated in package scripts and Docker commands without affecting Python dependency management |
| VIII. Frontend Server-First BFF Architecture | PASS | Design keeps Server Components as default, forbids client-side backend calls, reserves middleware/auth scaffolding, and defers Route Handlers until a browser-facing API need exists |
| IX. UI Styling & Design System Fidelity | PASS | Design cites the Editorial Index recipe plus Page Shell and Navigation patterns, with the empty-state substitution documented as the sole intentional deviation |

**Post-Phase 1 gate: PASS** — ready for `/speckit.tasks`.

## Complexity Tracking

> No constitution violations requiring justification.
