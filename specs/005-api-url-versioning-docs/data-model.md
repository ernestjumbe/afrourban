# Data Model: API URL Versioning and Documentation

**Feature**: 005-api-url-versioning-docs  
**Date**: 2026-03-28

This feature introduces governance and contract entities for routing and documentation. These are
conceptual entities used by configuration, schemas, and tests (not necessarily new database tables).

## Entity: APIVersion

Represents a published API namespace lifecycle.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `code` | string | required, unique (`v1`, `v2`) | Version identifier |
| `base_path` | string | required, unique | Version base path (for example `/api/v1/`) |
| `status` | enum | required (`active`, `deprecated`, `retired`) | Lifecycle state |
| `is_default` | boolean | required | Whether this is the default active version |
| `deprecation_date` | date | required when deprecated/retired | Public deprecation date |
| `removal_date` | date | required when deprecated/retired | Planned removal date |
| `migration_path` | string | required when deprecated/retired | Upgrade guidance link/text |

### Validation Rules

- Exactly one active version can be marked `is_default=true`.
- For deprecated/retired versions: `removal_date >= deprecation_date + 90 days`.
- `base_path` must be versioned and start with `/api/v`.

### State Transitions

```text
active -> deprecated -> retired
```

- `active -> deprecated`: requires deprecation metadata.
- `deprecated -> retired`: requires removal date reached.

## Entity: APIRouteRegistration

Represents one routable API operation registered through `api_urlpatterns`.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `route_name` | string | required | Stable route identifier |
| `method` | enum | required | HTTP method (`GET`, `POST`, `PATCH`, `PUT`, `DELETE`) |
| `relative_path` | string | required | Version-relative route path |
| `full_path` | string | derived, unique with method | Materialized path (for example `/api/v1/auth/register/`) |
| `permission_scope` | enum | required (`public`, `authenticated`, `staff`) | Access scope |
| `version_code` | string | required, FK -> `APIVersion.code` | Owning API version |
| `include_public_docs` | boolean | required | Whether route appears in public docs |
| `include_internal_docs` | boolean | required | Whether route appears in internal docs |
| `legacy_alias` | string/null | optional | Previous unversioned route (if existed) |
| `legacy_removed` | boolean | required | Whether legacy route was removed |

### Validation Rules

- Active routes must be registered under a versioned namespace (`/api/v{n}/...`).
- No duplicate `(method, full_path)` pairs.
- `include_internal_docs` must be `true` for all active routes.
- `include_public_docs` can be `true` only when `permission_scope=public`.
- `legacy_alias` must be absent or marked removed after this feature release.

## Entity: DocumentationView

Represents one published schema/documentation surface.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `view_type` | enum | required (`public`, `internal`) | Documentation audience |
| `schema_endpoint` | string | required | Endpoint returning OpenAPI schema |
| `ui_endpoint` | string | required | Endpoint rendering docs UI |
| `auth_requirement` | enum | required (`none`, `authenticated`) | Required access level |
| `included_scopes` | set | required | Route scopes included in the view |

### Validation Rules

- Public view includes only `public` scope routes.
- Internal view includes `public`, `authenticated`, and `staff` routes.
- Internal view requires authentication.

## Entity: DeprecationNotice

Represents a specific deprecation declaration for an API version or endpoint.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `target_type` | enum | required (`version`, `endpoint`) | What is being deprecated |
| `target_id` | string | required | Version code or route identifier |
| `deprecation_date` | date | required | Announcement date |
| `removal_date` | date | required | Effective removal date |
| `migration_path` | string | required | Client migration instructions |
| `status` | enum | required (`announced`, `active`, `completed`) | Notice lifecycle |

### Validation Rules

- `removal_date` must be at least 90 days after `deprecation_date`.
- `migration_path` must be non-empty and actionable.
- Deprecated items must have exactly one active notice entry.
