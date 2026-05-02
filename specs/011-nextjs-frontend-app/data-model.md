# Data Model: Initial Frontend Application

## 1. FrontendRuntimeConfig

Represents the validated runtime inputs required for the frontend service to boot and advertise its local URL correctly.

### Fields

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `port` | integer | yes | Defaults to `3030`; overrides must remain within `3030-4000` |
| `nodeEnv` | enum | yes | Allowed values: `development`, `test`, `production` |
| `siteUrl` | string | yes | Must resolve to the public frontend origin for the current environment |
| `apiUrl` | string | reserved | Server-only base URL for future BFF/auth work; must not be exposed directly to browser code unless intentionally public |
| `authSecret` | string | reserved | Required once Auth.js is activated for protected routes |

### Validation Rules

- Reject startup if `port` falls outside `3030-4000`.
- Reject startup if required current-environment fields are missing.
- Treat reserved auth fields as optional for this feature, but keep their schema slots documented.

### State Transitions

| State | Trigger | Next State |
|-------|---------|------------|
| `default` | No override provided | `validated` with port `3030` |
| `override-requested` | Override env provided | `validated` if in range, otherwise `invalid` |
| `invalid` | Schema validation fails | startup aborts with structured error |

## 2. SiteNavigationItem

Represents a single navigation entry in the launch navigation.

### Fields

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `label` | string | yes | Uses uppercase tracked sans treatment in the UI |
| `href` | string | yes | Must point only to implemented routes at launch |
| `isPrimary` | boolean | no | Marks the root or the main call-to-action destination |
| `visibility` | enum | yes | `visible` or `hidden`; unfinished destinations are omitted rather than shown disabled |

### Validation Rules

- Navigation entries for unfinished routes must not be rendered as clickable links.
- The initial launch navigation must include only implemented destinations.
- Navigation must remain keyboard reachable across desktop and mobile layouts.

## 3. HomepageShell

Represents the shared editorial frame used by the root route and future public pages.

### Fields

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `theme` | enum | yes | Default is dark-first |
| `goldTrimHeight` | integer | yes | Must remain `6px` per the component guide |
| `navigationItems` | list of `SiteNavigationItem` | yes | Provided by shared configuration |
| `backgroundTreatment` | enum | yes | Low-contrast pattern or atmospheric background only |
| `contentWidth` | string | yes | Must stay within the documented wide-shell constraint |

### Relationships

- Owns one ordered collection of `SiteNavigationItem` values.
- Wraps exactly one homepage content state for this feature.

## 4. HomepageEmptyState

Represents the intentionally empty content module rendered in place of editorial cards or featured content.

### Fields

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `eyebrow` | string | no | Short contextual label using tracked sans styling |
| `headline` | string | yes | Serif-led narrative heading |
| `body` | string | yes | Explains the launch state without fake content or placeholder listings |
| `supportingNote` | string | no | Optional secondary copy about what arrives next |
| `actions` | list | no | May be empty for this bootstrap feature |

### Validation Rules

- Copy must describe the current launch state truthfully.
- Empty-state content must remain fully functional when the backend API is unavailable.
- The module must work in desktop and mobile layouts without horizontal scrolling.