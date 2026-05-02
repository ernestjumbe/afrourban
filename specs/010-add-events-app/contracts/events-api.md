# Events API Contract

**Feature**: 010-add-events-app  
**Date**: 2026-04-27

## 1. Namespace and Routing Contract

1. All event routes live under `/api/v1/events/`.
2. Routes are defined in `events.urls.api_v1_urlpatterns`.
3. Main `afrourban/urls.py` includes the event routes through `api_v1_module_urlpatterns` and
   `api_urlpatterns` under `/api/`.
4. OpenAPI documentation must be regenerated with drf-spectacular (OpenAPI 3.0+).
5. Because all event endpoints are authenticated in v1, they appear in the internal schema and
   remain absent from the public schema.

## 2. Authentication and Permission Contract

- All events endpoints are authenticated in v1.
- Any authenticated user may create a personal event.
- Only the current owner of an organization may create or update an event on behalf of that
  organization.
- Any authenticated user may read event detail in v1.
- Cover-image mutations follow the same write-permission rules as metadata updates.
- Validation and permission failures use the project’s RFC 9457 Problem Details error envelope.

## 3. Create Contract

### Endpoint

- `POST /api/v1/events/`

### Request Body

| Field | Required | Rules |
|-------|----------|-------|
| `organization_id` | conditional | omit for personal events; required only when creating an organization-owned event |
| `title` | yes | trimmed text, max 255 chars |
| `description` | yes | max 1000 chars |
| `category` | no | one supported category choice; defaults to `other` |
| `start_at` | yes | ISO 8601 datetime |
| `end_at` | yes | ISO 8601 datetime later than `start_at` |
| `location` | yes | nested object described below |
| `tickets_url` | no | valid URL |

### Location Object

| Field | Required | Rules |
|-------|----------|-------|
| `type` | yes | `physical` or `web` |
| `web_url` | conditional | required when `type=web` |
| `country` | conditional | required when `type=physical` |
| `state` | conditional | required when `type=physical` |
| `city` | conditional | required when `type=physical` |
| `postcode` | conditional | required when `type=physical` |

### Behavior

- If `organization_id` is omitted, the event is created as a personal event under `request.user`.
- If `organization_id` is supplied, the acting user must own that organization.
- Create requests do not accept `cover_image`; cover media is handled by dedicated endpoints.
- The response includes organizer context, current location state, and current cover-image URL when
  present.

### Success Response

- Returns HTTP `201 Created` with the full event detail object.

## 4. Detail and Update Contract

### Endpoints

- `GET /api/v1/events/{event_id}/`
- `PATCH /api/v1/events/{event_id}/`

### Detail Response

Returns the full event detail object:

| Field | Description |
|-------|-------------|
| `id` | Event id |
| `organizer_type` | `person` or `organization` |
| `owner_user_id` | Owning user id for personal events or `null` |
| `organization_id` | Owning organization id for organization events or `null` |
| `title` | Event title |
| `description` | Event description |
| `category` | Stored category value |
| `start_at` | Event start datetime |
| `end_at` | Event end datetime |
| `location` | Structured current location object |
| `cover_image_url` | Absolute cover URL or `null` |
| `tickets_url` | Tickets URL or `null` |
| `created_at` | Creation timestamp |
| `updated_at` | Last modification timestamp |

### Update Request Body

All metadata fields are optional for patch operations except organizer context, which is immutable:

| Field | Rules |
|-------|-------|
| `title` | if supplied, trimmed text, max 255 chars |
| `description` | if supplied, max 1000 chars |
| `category` | if supplied, must be a supported category |
| `start_at` | if supplied, resulting schedule must remain valid |
| `end_at` | if supplied, resulting schedule must remain valid |
| `location` | if supplied, must be a complete valid location object for the chosen type |
| `tickets_url` | if supplied, must be a valid URL or explicit null to clear |
| `organization_id` | must not be accepted as an update field |

### Audit Contract

- Successful changes to `title`, `start_at`, `end_at`, and `location` create immutable audit rows.
- Audit persistence is required even though audit history is not returned in the standard event
  detail payload.
- Non-audited fields such as `description`, `category`, `tickets_url`, and `cover_image` do not
  create audit rows.

### Permission Contract

- The personal event owner may update their event.
- The current owner of the event’s organization may update an organization-owned event.
- Unauthorized update attempts return HTTP `403 Forbidden`.

## 5. Cover Image Contract

### Endpoints

- `POST /api/v1/events/{event_id}/cover/`
- `DELETE /api/v1/events/{event_id}/cover/`

### Upload Request Contract

| Endpoint | Content Type | Field |
|----------|--------------|-------|
| `POST .../cover/` | `multipart/form-data` | `cover_image` |

### Upload Validation

- Allowed formats: JPEG, PNG, WebP
- Maximum file size: 5MB
- Write permissions match the event metadata update permissions

### Upload Success Contract

| Field | Description |
|-------|-------------|
| `asset_url` | Absolute URL of the uploaded cover image |
| `message` | Human-readable success message |

### Delete Success Contract

- Returns HTTP `204 No Content`

## 6. Error Contract

Validation and permission errors use Problem Details fields:

| Field | Description |
|-------|-------------|
| `type` | Problem type URI (`about:blank` by default) |
| `title` | Human-readable HTTP error title |
| `status` | HTTP status code |
| `detail` | Summary of validation or permission failure |
| `instance` | Request path |
| `errors` | Field-level validation details when applicable |

Expected failure cases:

- `end_at` is not later than `start_at`
- `description` exceeds 1000 characters
- physical location is missing `country`, `state`, `city`, or `postcode`
- web location is missing `web_url`
- unauthorized organization selection on create
- unauthorized metadata or cover-image mutation attempt
- attempt to change organizer context after creation
- unsupported cover-image type or oversized upload

## 7. Documentation, Compatibility, and Deprecation

1. Internal schema and endpoint inventory documentation must include all events endpoints.
2. Public schema must continue to exclude events endpoints because they require authentication.
3. This is an additive `/api/v1/` feature and does not deprecate any existing route.
4. Event listing/discovery, anonymous public event reads, organizer transfer, recurrence,
   cancellation workflows, and end-user audit-history browsing are not part of this iteration’s API
   contract.
