# Frontend

This workspace contains the repository's Next.js App Router frontend.

## Local development

Start the frontend on the default port:

```bash
NODE_ENV=development SITE_URL=http://localhost:3030 npm run dev -- --hostname 0.0.0.0 --port 3030
```

Use a supported override from `3030` through `4000` when needed:

```bash
FRONTEND_PORT=3031 SITE_URL=http://localhost:3031 NODE_ENV=development npm run dev -- --hostname 0.0.0.0 --port 3031
```

## Required runtime variables

- `NODE_ENV`
- `SITE_URL`
- `FRONTEND_PORT` optional, default `3030`

Reserved variables for future BFF/auth work:

- `API_URL`
- `AUTH_SECRET`
- `AUTH_TRUST_HOST`

## Ownership boundaries

- `src/components/page-shell.tsx` and `src/components/site-navigation.tsx` are shared primitives for full-page Design 4 framing and launch navigation.
- `src/components/home-hero.tsx` and `src/components/home-empty-state.tsx` are route-local presentation modules. They accept content props and should not own shared site config.
- `src/app/page.tsx` owns homepage-specific copy and composition.

## Reserved future extension points

- `src/lib/env.ts` exposes `getReservedServerConfig()` for future server-side BFF and Auth.js work without forcing those integrations into the public homepage now.
- `src/lib/site-config.ts` keeps live launch navigation separate from reserved future destinations and route prefixes.
- `src/proxy.ts` sets request context headers and marks reserved protected route prefixes without blocking the current public experience.

## Quality checks

```bash
npm run lint
npm run typecheck
npm run test
npm run test:e2e
npm run build
```