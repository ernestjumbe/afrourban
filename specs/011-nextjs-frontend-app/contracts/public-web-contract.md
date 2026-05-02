# Contract: Public Web Bootstrap

## 1. Public Route Contract

### Route

- **Method**: `GET`
- **Path**: `/`
- **Audience**: Unauthenticated public visitors and local contributors

### Response Contract

- Returns `200 OK` with server-rendered HTML.
- Must include a Design 4 page shell with:
  - gold trim
  - sticky navigation
  - concise introductory hero
  - intentional empty-state content
- Must not require any live backend content fetch to render the delivered launch state.

### Navigation Contract

- Navigation renders only implemented destinations at launch.
- Unimplemented routes are omitted rather than shown as broken or disabled links.
- Mobile navigation remains keyboard reachable and must not introduce horizontal scrolling.

## 2. Runtime Configuration Contract

### Required Current Inputs

| Variable | Scope | Contract |
|----------|-------|----------|
| `FRONTEND_PORT` | compose/runtime | Optional; defaults to `3030`; if provided, must be an integer in the `3030-4000` range |
| `SITE_URL` | server/runtime | Required for environment-aware absolute URL generation and local docs clarity |
| `NODE_ENV` | server/runtime | Required and must match the current execution environment |

### Reserved Future Inputs

| Variable | Scope | Contract |
|----------|-------|----------|
| `API_URL` | server/runtime | Reserved for future server-side BFF and Auth.js calls to Django |
| `AUTH_SECRET` | server/runtime | Reserved for future Auth.js session encryption |
| `AUTH_TRUST_HOST` | server/runtime | Reserved for future Auth.js deployment/runtime configuration |

### Failure Contract

- Invalid runtime inputs must fail application startup before the server begins accepting requests.
- Startup failures must emit structured server-side logs rather than silent fallback behavior.

## 3. Local Docker Compose Contract

- The `frontend` service participates in the default `docker-compose.local.yml` startup path.
- The service exposes the application on its own port instead of proxying through Django.
- Default local URL: `http://localhost:3030`.
- Port overrides remain within the `3030-4000` range and must be reflected in the documented startup instructions.

## 4. Validation Contract

Before the feature is considered complete, the implementation must pass:

- ESLint with `next/core-web-vitals`
- TypeScript strict type checking
- Vitest coverage for shared config and homepage shell behavior
- Playwright smoke coverage for homepage render and mobile layout
- `next build` with standalone output