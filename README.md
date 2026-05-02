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

## Local Frontend Startup

The repository now includes a dedicated Next.js frontend service in the default local compose stack.

### Start the full local stack

```bash
docker compose -f docker-compose.local.yml up --build --remove-orphans
```

Expected local URLs:

- Django API: `http://localhost:8000`
- Frontend: `http://localhost:3030`

### Override the frontend port

Choose any port from `3030` through `4000`:

```bash
FRONTEND_PORT=3031 docker compose -f docker-compose.local.yml up --build --remove-orphans
```

When stopping the stack after service-name changes, use:

```bash
docker compose -f docker-compose.local.yml down --remove-orphans
```

### Run frontend checks directly

```bash
cd frontend
npm run lint
npm run typecheck
npm run test
npm run test:e2e
npm run build
```

## Frontend Ownership Boundaries

- Shared shell primitives live in `frontend/src/components/page-shell.tsx` and `frontend/src/components/site-navigation.tsx`.
- Route-local homepage copy and composition live in `frontend/src/app/page.tsx`, with presentational homepage modules in `frontend/src/components/home-hero.tsx` and `frontend/src/components/home-empty-state.tsx`.
- Reserved future extension points for BFF and Auth.js work live in `frontend/src/lib/env.ts`, `frontend/src/lib/site-config.ts`, and `frontend/src/proxy.ts` so contributors do not have to invent their own auth or proxy seams later.
