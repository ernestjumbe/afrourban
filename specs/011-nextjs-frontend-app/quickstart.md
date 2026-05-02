# Quickstart: Initial Frontend Application

## Prerequisites

- Docker Desktop or compatible local Docker runtime
- Existing backend project dependencies installed through Poetry
- No service already bound to local port `3030`, unless a supported override is provided

## 1. Start the default local stack

Run the repository’s default local compose workflow after the frontend service is added:

```bash
docker compose -f docker-compose.local.yml up --build --remove-orphans
```

Expected outcome:

- Django remains reachable on `http://localhost:8000`
- The frontend becomes reachable on `http://localhost:3030`
- The homepage renders even if no backend content data is available

## 2. Override the frontend port when `3030` is unavailable

Choose any port in the `3030-4000` range:

```bash
FRONTEND_PORT=3031 docker compose -f docker-compose.local.yml up --build --remove-orphans
```

Expected outcome:

- The frontend binds to the chosen override port
- Documentation and runtime validation continue to reject values outside `3030-4000`

## 3. Run frontend validation gates

Use the frontend package scripts once the app has been scaffolded:

```bash
cd frontend
npm run lint
npm run typecheck
npm run test
npm run test:e2e
npm run build
```

Expected outcome:

- Lint passes with `next/core-web-vitals`
- TypeScript strict mode passes without unsafe escape hatches
- Vitest confirms runtime config and homepage shell behavior
- Playwright confirms homepage render and mobile layout
- `next build` produces standalone output without runtime errors

## 4. Run backend-side checks only if supporting backend files change

If implementation touches Python files, settings, or backend documentation helpers, run the existing Poetry-managed checks:

```bash
poetry run ruff check .
poetry run mypy .
poetry run pytest
```

API schema validation is not required for this feature because no Django API endpoints change.

## 5. Verify the delivered user experience

- Open the public root route in desktop and mobile-sized viewports
- Confirm the page shows the Design 4 shell, minimal launch navigation, intro content, and intentional empty state
- Confirm the page remains usable when backend content services are unavailable

## 6. Final validation notes

Validated on 2026-05-02.

- Visual QA pass: verified the homepage in a live browser with the Design 4 shell, launch-only navigation, intentional empty state, mobile menu visibility, and no horizontal overflow.
- Accessibility refinements applied: skip link, stronger keyboard focus states, and reduced-motion handling.
- `cd frontend && npm run lint`: passed.
- `cd frontend && npm run typecheck`: passed.
- `cd frontend && npm run test`: passed.
- `cd frontend && npm run test:e2e`: passed.
- `cd frontend && NODE_ENV=production SITE_URL=http://localhost:3030 FRONTEND_PORT=3030 npm run build`: passed and produced standalone output.
- `docker compose -f docker-compose.local.yml up --build --remove-orphans`: rerun succeeded; the frontend image built, the stack attached successfully, the homepage served on `http://localhost:3030`, Django returned `200` from `/api/v1/health/`, and the legacy `afrourban-web-1` orphan warning was cleared.
- Residual backend warnings remain outside the frontend bootstrap scope: Flower may briefly time out before the worker registers, and the Celery worker still warns about running as root inside the container.