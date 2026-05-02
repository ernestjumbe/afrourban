# Research: Events App

**Feature**: 010-add-events-app  
**Date**: 2026-04-27

## 1. App Naming and Placement

### Decision

Create a new first-class Django app named `events` and register it alongside `users`, `profiles`,
`organizations`, and `health`.

### Rationale

The feature introduces a distinct domain with its own persistence, validation, permissions, media,
and audit requirements. A dedicated app keeps event logic separate from person profiles and
organization profiles while matching the project’s existing app-by-domain architecture and required
HackSoft-style layout.

### Alternatives considered

- Extend `profiles`: rejected because event ownership, timing, and audit concerns are not profile
  responsibilities.
- Extend `organizations`: rejected because the feature must support both personal events and
  organization-owned events.

## 2. Organizer Ownership Model

### Decision

Represent each event in a single `Event` model with exactly one organizer context:

- personal event: owned by one registered user
- organization event: owned by one organization

The organizer context is immutable after creation. Organization-event writes reuse the existing
`is_organization_owner` helper to verify that the acting user owns the selected organization.

### Rationale

A single model keeps the API and persistence surface small while still expressing the two organizer
types in the approved scope. Freezing organizer context after creation prevents complicated transfer
rules, avoids ambiguous audit stories, and aligns with the feature’s focus on creating and
maintaining events rather than reassigning them.

### Alternatives considered

- Separate `PersonalEvent` and `OrganizationEvent` models: rejected because it duplicates nearly
  all fields, serializers, and service logic for little benefit.
- Allow organizer reassignment after creation: rejected because the specification does not require
  transfer workflows and they would complicate permissions and audit history.
- Use a generic foreign key to any organizer type: rejected as unnecessary indirection for only two
  known organizer contexts.

## 3. Event Category and Title Policy

### Decision

Use a predefined event-category list with `other` as the default and keep the initial set small:

- `music`
- `food_drink`
- `arts_culture`
- `community`
- `sports_fitness`
- `business_networking`
- `education_workshop`
- `other`

Store titles as required trimmed text with a conventional maximum length of 255 characters.

### Rationale

A small curated list satisfies the specification’s requirement for a default `Other` category
without over-designing taxonomy management. A 255-character title limit matches existing naming
patterns in the codebase and is more than sufficient for event titles while remaining simple to
validate and index.

### Alternatives considered

- Free-text categories: rejected because the specification implies a defaultable category choice and
  free-text values would be inconsistent and harder to filter later.
- A large exhaustive category catalog: rejected because the current feature does not justify
  taxonomy-management complexity.
- Unlimited title length: rejected because titles are short labels and should remain predictable for
  validation and API consumers.

## 4. Location Modeling

### Decision

Model event location as a mutually exclusive state on the event record:

- `location_type=physical` with required `country`, `state`, `city`, and `postcode`
- `location_type=web` with required `web_url`

Store physical-location components directly on the `Event` model, clear the non-applicable location
fields on write, and expose the API contract as a nested `location` object.

### Rationale

This approach matches the specification exactly, keeps validation deterministic, and avoids
introducing a second persistence table for a location object that has no lifecycle independent of
its event. Clearing incompatible fields prevents stale contradictory data when a location changes
between web and physical modes.

### Alternatives considered

- A separate `EventLocation` model: rejected because location has a strict one-to-one lifecycle with
  the event and does not need independent querying in this scope.
- A single free-text `location` field: rejected because the specification requires structured
  physical-address components and web addresses to be validated differently.
- Allow both physical and web data at the same time: rejected because the specification describes
  the location as physical address or web address, not both simultaneously.

## 5. Cover Image Handling

### Decision

Keep event metadata writes JSON-based and manage the optional `cover_image` through dedicated
multipart endpoints:

- `POST /api/v1/events/{event_id}/cover/`
- `DELETE /api/v1/events/{event_id}/cover/`

Reuse the same file constraints already used elsewhere in the project: JPEG/PNG/WebP and maximum
5MB.

### Rationale

Dedicated media endpoints keep the create/update serializers focused on event metadata and location
rules, avoid mixed JSON/multipart parsing on the main mutation endpoints, and reuse the project’s
existing patterns for optional image assets.

### Alternatives considered

- Accept multipart payloads on create and update: rejected because it complicates validation,
  request parsing, and test setup for little business value.
- Store cover-image metadata in a separate model: rejected because one optional file field does not
  justify an extra table.

## 6. Audit History Strategy

### Decision

Persist audited changes in a dedicated first-party `EventAuditEntry` model. Each successful update
creates one immutable audit row per changed audited field among:

- `title`
- `start_at`
- `end_at`
- `location`

Each audit row stores the field name, previous normalized value, new normalized value, actor, event,
and timestamp.

### Rationale

The feature’s audit scope is narrow and explicit, so a small first-party audit table is simpler
than adopting a history package that would capture unrelated fields and introduce broader migration
and admin complexity. Per-field audit rows also make it easy to preserve transitions between web
and physical location formats in a normalized way.

### Alternatives considered

- Adopt `django-simple-history` or a similar package: rejected because the project does not already
  use it and the requested audit scope is much narrower than full-record history.
- Store whole-record JSON snapshots on each update: rejected because it would duplicate unchanged
  data and make targeted audit review harder.
- Log audits only to structured logs: rejected because logs do not satisfy durable event-lifetime
  retention.

## 7. API Surface and Visibility

### Decision

Expose the following authenticated routes under `/api/v1/events/`:

- `POST /api/v1/events/`
- `GET /api/v1/events/{event_id}/`
- `PATCH /api/v1/events/{event_id}/`
- `POST /api/v1/events/{event_id}/cover/`
- `DELETE /api/v1/events/{event_id}/cover/`

Publish these routes in the internal schema only. Do not introduce a broader list/discovery
endpoint in this iteration.

### Rationale

The approved feature scope centers on creation and maintenance, not on discovery, search, or public
browsing. Keeping the v1 surface to create/detail/update plus cover media delivers the required
behavior without speculating about visibility, filtering, pagination, or sorting rules that the
current specification does not define.

### Alternatives considered

- Add `GET /api/v1/events/` now with filtering and pagination: rejected because discovery behavior,
  default visibility, and event-browsing rules are not defined in the approved scope.
- Publish anonymous public event reads in v1: rejected because existing API defaults are
  authenticated and the approved specification does not require public exposure.

## 8. Observability and Test Strategy

### Decision

Add structured logs and automated coverage for:

- personal and organization event creation success/failure
- owner-vs-non-owner organization event authorization outcomes
- schedule and location validation failures
- audited field-change creation on updates
- cover-image upload, replace, and delete outcomes
- versioned routing and schema publication

### Rationale

This matches the constitution’s structured observability and test-first requirements while focusing
tests on the feature’s regression-prone rules: exclusive ownership, location-mode switching,
schedule validation, and immutable audit persistence.

### Alternatives considered

- Only test API happy paths: rejected because service-level audit and ownership rules are central
  business logic and need direct coverage.
- Rely on generic Django logging only: rejected because the project standard is structured logging
  with business-relevant fields.
