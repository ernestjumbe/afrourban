# afrourban Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-27

## Active Technologies
- Python 3.11 (project constraint `^3.11`) + Django 5.1.2, Django REST Framework, SimpleJWT, drf-spectacular, structlog (006-add-username-privacy)
- Django ORM on PostgreSQL (production) / SQLite (dev+test), with new user-field migration (006-add-username-privacy)
- Python 3.11 (project constraint `^3.11`) + Django 5.1.2, Django REST Framework 3.17.1, drf-spectacular 0.29.0, structlog, SimpleJWT (existing project auth stack) (007-health-endpoint)
- Existing PostgreSQL (production) / SQLite (dev+test); no new persistent tables or migrations required (007-health-endpoint)
- Python 3.11 (project constraint `^3.11`) + Django 5.1.2, Poetry, pytest, Ruff, mypy, plus new `pre-commit` dev dependency (008-backend-precommit-hooks)
- Python 3.11 (project constraint `^3.11`) + Django 5.1.2, Django REST Framework 3.17.1, drf-spectacular 0.29.0, SimpleJWT 5.5.1, Pillow 12.1.1, structlog 25.2.0 (009-organization-profiles)
- Django ORM on PostgreSQL (production) / SQLite (dev+test), with one new `organizations_organization` table and media file references for logo/cover assets (009-organization-profiles)
- Django ORM on PostgreSQL (production) / SQLite (dev+test), with new `events_event` and `events_eventauditentry` tables plus media file references for optional cover images (010-add-events-app)

- Python 3.11 + Django 5.1.2, Django REST Framework, SimpleJWT, drf-spectacular, structlog (005-api-url-versioning-docs)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.11: Follow standard conventions

## Recent Changes
- 010-add-events-app: Added Python 3.11 (project constraint `^3.11`) + Django 5.1.2, Django REST Framework 3.17.1, drf-spectacular 0.29.0, SimpleJWT 5.5.1, Pillow 12.1.1, structlog 25.2.0
- 009-organization-profiles: Added Python 3.11 (project constraint `^3.11`) + Django 5.1.2, Django REST Framework 3.17.1, drf-spectacular 0.29.0, SimpleJWT 5.5.1, Pillow 12.1.1, structlog 25.2.0
- 008-backend-precommit-hooks: Added Python 3.11 (project constraint `^3.11`) + Django 5.1.2, Poetry, pytest, Ruff, mypy, plus new `pre-commit` dev dependency


<!-- MANUAL ADDITIONS START -->
## Constitution Overrides

- Frontend work MUST use Next.js App Router under `frontend/src/app`; Pages Router usage is forbidden.
- Frontend route segments MUST colocate route-local components, logic, and types.
- React Server Components MUST be the default; add `'use client'` only for browser APIs, event handlers, or client hooks.
- The Next.js server MUST act as the BFF. Client code MUST NOT call the external Django API directly.
- Frontend authentication MUST use Auth.js v5 Credentials against the Django API with encrypted session token storage and server-side refresh rotation.
- Frontend validation and quality gates MUST use Zod, TypeScript strict mode, ESLint `next/core-web-vitals`, Vitest, Playwright, and `next build` with `output: 'standalone'`.
- Frontend UI MUST follow AfroUrban Design 4 guidance in `guide/FRONTEND_DESIGN_SYSTEM.md`, `guide/COMPONENT_GUIDE.md`, and `guide/RECIPES.md`.
- Pages MUST use the closest documented recipe and preserve the dark-first editorial visual language: gold trim, serif narrative headings, uppercase tracked sans UI, gold primary actions, terracotta category accents, restrained motion, and no dashboard/SaaS styling drift.
<!-- MANUAL ADDITIONS END -->
