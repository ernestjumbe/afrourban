# Research: Organization Profiles

**Feature**: 009-organization-profiles  
**Date**: 2026-04-25

## 1. App Naming and Placement

### Decision

Create a new first-class Django app named `organizations` and register it alongside `users`,
`profiles`, and `health`.

### Rationale

`organizations` is broader and more accurate than `businesses` because the feature must represent
not only commercial entities but also communities and crews such as event organizers and dance
crews. A dedicated app preserves the architectural separation between human user profiles and
organization entities required by the feature.

### Alternatives considered

- Name the app `businesses`: rejected because it narrows the domain and does not fit
  non-commercial groups such as dance crews or online communities.
- Extend `profiles.Profile`: rejected because the feature explicitly requires organization entities
  to remain distinct from individual people.

## 2. Organization Name Uniqueness Policy

### Decision

Enforce case-insensitive uniqueness of organization `name` per owner, while allowing the same
public name to appear under different owners.

### Rationale

Per-owner uniqueness prevents accidental duplicate records for the same account without imposing an
unrealistic global uniqueness rule on common business names. This works cleanly with ID-based
organization routes and the current scope, which does not include slugs or multi-location records.

### Alternatives considered

- Global case-insensitive uniqueness: rejected because common names can legitimately recur across
  different owners and locations.
- No uniqueness at all: rejected because, with single-owner and single-location scope, duplicate
  names under one owner are more likely to be user error than intended behavior.

## 3. API Surface and Access Model

### Decision

Expose an authenticated versioned resource under `/api/v1/organizations/` with:

- `GET /api/v1/organizations/` for paginated collection reads
- `POST /api/v1/organizations/` for creation
- `GET /api/v1/organizations/{organization_id}/` for detail reads
- `PATCH /api/v1/organizations/{organization_id}/` for owner-only updates
- Separate logo/cover upload and delete endpoints under the same organization resource

Collection reads support filtering, pagination, and sorting with query parameters rather than
separate owner-specific endpoints.

### Rationale

This satisfies the constitution’s API-first requirement and matches the repository’s current DRF
APIView and manual pagination patterns. Authenticated-only reads align with the project’s existing
default permission posture while still supporting community-facing browsing for signed-in users.

### Alternatives considered

- Anonymous public reads in v1: rejected because current API defaults are authenticated and the
  approved feature spec does not require anonymous exposure.
- A `/mine/` collection route: rejected because `owner_scope=mine` on the collection keeps the
  surface smaller while still supporting owner views.
- Include `DELETE /api/v1/organizations/{id}/` now: rejected because the approved feature spec
  scope covers create, view, and update flows only.

## 4. Presence Mode and Address Handling

### Decision

Treat `is_online_only` as the source of truth for presence mode:

- when `is_online_only=false`, `physical_address` is required
- when `is_online_only=true`, `physical_address` is optional and should be cleared on write to
  avoid stale contradictory data

### Rationale

This yields deterministic validation and avoids storing a physical storefront address on records
that are intentionally marked online-only.

### Alternatives considered

- Allow online-only organizations to keep an old physical address: rejected because it creates
  conflicting public data.
- Require `physical_address` in all cases: rejected because it contradicts the feature’s support
  for online-only organizations.

## 5. Branding Upload Strategy

### Decision

Keep organization metadata writes JSON-based and manage `logo` and `cover_image` through dedicated
multipart endpoints, reusing the existing avatar-upload conventions:

- JPEG/PNG/WebP only
- maximum 5MB per upload
- separate upload/delete behavior for logo and cover image

### Rationale

Separate media endpoints keep create/update serializers simple, avoid mixed JSON/multipart handling
on the main organization mutation endpoints, and fit the project’s current profile-avatar pattern.

### Alternatives considered

- Accept multipart on the main create/update endpoints: rejected because it complicates validation
  and diverges from the current app structure.
- Store branding in a separate model: rejected as unnecessary complexity for only two optional
  image fields.

## 6. Filtering, Pagination, and Sorting Contract

### Decision

Define the organization collection endpoint with these query controls:

- `owner_scope=all|mine`
- `organization_type=<choice>`
- `is_online_only=true|false`
- `search=<name or description fragment>`
- `ordering=name|-name|created_at|-created_at`
- `page` and `page_size` with default `20` and max `100`

### Rationale

This satisfies the constitution’s collection-endpoint requirements while staying consistent with the
manual pagination already used in admin user listing.

### Alternatives considered

- No pagination because data volume is initially small: rejected because pagination is a
  constitutional requirement.
- Support many sort fields immediately: rejected to keep the contract small and predictable.

## 7. Observability and Test Strategy

### Decision

Add structured logs and automated coverage for:

- organization create/update success and validation failures
- owner-vs-non-owner mutation outcomes
- logo/cover upload, replace, and delete operations
- collection filtering/pagination/sorting behavior
- schema and `/api/v1/` routing coverage

### Rationale

This matches the constitution’s structured observability and test-first requirements and keeps the
feature safe as a new app introducing both media handling and ownership rules.

### Alternatives considered

- Only test happy paths: rejected because ownership and conditional address logic are regression
  prone.
- Rely on generic Django logging only: rejected because the project standard is structured logging
  with meaningful business-event fields.
