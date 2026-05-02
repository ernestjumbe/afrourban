# Data Model: Events App

**Feature**: 010-add-events-app  
**Date**: 2026-04-27

This feature introduces event records that may be owned either by an individual user or by an
organization, plus immutable audit records for selected event-field changes. Entities below are
conceptual and map to Django models, serializers, and service-layer commands.

## Entity: Event

Represents a scheduled activity created either by a registered user or on behalf of an owned
organization.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | integer | primary key | Event identifier |
| `owner_user_id` | integer/null | required for personal events; null for organization events | User who owns a personal event |
| `organization_id` | integer/null | required for organization events; null for personal events | Organization that owns the event |
| `title` | string | required, max 255 chars | Public event title |
| `description` | string | required, max 1000 chars | Event description |
| `category` | enum | required, default `other` | One of `music`, `food_drink`, `arts_culture`, `community`, `sports_fitness`, `business_networking`, `education_workshop`, `other` |
| `start_at` | datetime | required | Event start date and time |
| `end_at` | datetime | required, must be later than `start_at` | Event end date and time |
| `location_type` | enum | required, `physical` or `web` | Active location mode |
| `location_web_url` | string/null | required when `location_type=web`; null otherwise | Event web address |
| `location_country` | string/null | required when `location_type=physical` | Physical-location country |
| `location_state` | string/null | required when `location_type=physical` | Physical-location state/region |
| `location_city` | string/null | required when `location_type=physical` | Physical-location city/town |
| `location_postcode` | string/null | required when `location_type=physical` | Physical-location postcode/zipcode |
| `cover_image` | image/null | optional, JPEG/PNG/WebP, max 5MB | Optional event cover image |
| `tickets_url` | string/null | optional, valid URL | Optional ticket-purchase or registration link |
| `created_at` | datetime | required | Creation timestamp |
| `updated_at` | datetime | required | Last modification timestamp |

### Validation Rules

- Exactly one organizer context must be present: either `owner_user_id` or `organization_id`.
- Organizer context is immutable after creation; personal events do not become organization events
  and organization events do not become personal events in this scope.
- `title` is mandatory and stored as trimmed text.
- `description` is mandatory and must not exceed 1000 characters.
- `end_at` must be later than `start_at`.
- `category` defaults to `other` when omitted.
- If `location_type=web`, `location_web_url` is required and all physical-location fields are
  cleared before persistence.
- If `location_type=physical`, `location_country`, `location_state`, `location_city`, and
  `location_postcode` are required and `location_web_url` is cleared before persistence.
- `cover_image` is optional and independently managed.
- `tickets_url` is optional.

### State Transitions

#### Organizer Context

```text
PersonalOwned --(no organizer transfer supported)--> PersonalOwned
OrganizationOwned --(no organizer transfer supported)--> OrganizationOwned
```

#### Location Mode

```text
WebLocation --(replace with physical address)--> PhysicalLocation
PhysicalLocation --(replace with web URL)--> WebLocation
```

- Switching location mode is allowed and is audited as a `location` change.
- Inactive location fields are cleared during a successful transition.

## Entity: EventAuditEntry

Represents one immutable audit record for a tracked event-field change.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | integer | primary key | Audit-entry identifier |
| `event_id` | integer | required, foreign key to event | Event whose field changed |
| `field_name` | enum | required, one of `title`, `start_at`, `end_at`, `location` | Tracked field that changed |
| `old_value` | string | required | Previous normalized value |
| `new_value` | string | required | New normalized value |
| `actor_user_id` | integer | required | User who performed the update |
| `changed_at` | datetime | required | Timestamp of the change |

### Validation Rules

- Audit entries are append-only and are never updated or deleted by normal feature flows.
- A successful event update creates one audit row per changed audited field.
- If a field is submitted without an effective value change, no audit row is created for that field.
- Location audit values capture the normalized full location state so changes between `web` and
  `physical` remain reviewable.

## Entity: EventCoverCommand

Represents one cover-image upload or delete action.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `event_id` | integer | required | Target event |
| `actor_user_id` | integer | required | User attempting the cover mutation |
| `file` | image/null | required for upload; null for delete | Uploaded cover image |
| `message` | string | derived | Human-readable mutation outcome |

### Validation Rules

- Only the personal event owner may mutate a personal event’s cover image.
- Only the current owner of the event’s organization may mutate an organization event’s cover
  image.
- Uploads must be valid JPEG, PNG, or WebP files and must not exceed 5MB.
- Uploading a new cover image replaces the previous one.
- Deleting a missing cover image is treated as a safe no-op response.

## Entity: EventDetailProjection

Represents the detail payload returned after create, read, and update operations.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | integer | required | Event identifier |
| `organizer_type` | enum | required, `person` or `organization` | Organizer context type |
| `owner_user_id` | integer/null | conditional | Present for personal events |
| `organization_id` | integer/null | conditional | Present for organization events |
| `title` | string | required | Public event title |
| `description` | string | required | Event description |
| `category` | string | required | Stored category value |
| `start_at` | datetime | required | Event start date and time |
| `end_at` | datetime | required | Event end date and time |
| `location` | object | required | Structured location object for either web or physical mode |
| `cover_image_url` | string/null | optional | Absolute cover-image URL |
| `tickets_url` | string/null | optional | Optional tickets link |
| `created_at` | datetime | required | Creation timestamp |
| `updated_at` | datetime | required | Last modification timestamp |

### Projection Rules

- Detail payloads expose organizer context and current event metadata only.
- Standard event detail payloads do not embed audit history in this iteration.
- `cover_image_url` is returned as an absolute URL when a cover image exists.
