# Data Model: Organization Profiles

**Feature**: 009-organization-profiles  
**Date**: 2026-04-25

This feature introduces a dedicated organization domain that is separate from individual user
profiles. Entities below are conceptual and map to Django models, serializers, query parameters,
and service-layer commands.

## Entity: Organization

Represents a business, venue, crew, or online community owned by a registered user.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | integer | primary key | Organization identifier |
| `owner_id` | integer | required, foreign key to authenticated user | User who manages the organization |
| `name` | string | required, max 255 chars, case-insensitive unique per owner | Public organization name |
| `description` | string | required, non-empty | Public organization bio/description |
| `organization_type` | enum | required | One of `restaurant`, `barber`, `hair_salon`, `bar`, `night_club`, `event_organizer`, `dance_crew`, `online_community`, `retail_store`, `other` |
| `is_online_only` | boolean | required, default `false` | Presence-mode flag |
| `physical_address` | string/null | required when `is_online_only=false`; null/blank when `is_online_only=true` | Physical location text |
| `logo` | image/null | optional, JPEG/PNG/WebP, max 5MB | Organization logo |
| `cover_image` | image/null | optional, JPEG/PNG/WebP, max 5MB | Organization cover/banner image |
| `created_at` | datetime | required | Creation timestamp |
| `updated_at` | datetime | required | Last modification timestamp |

### Validation Rules

- An organization must always belong to exactly one owner.
- A single owner may have multiple organizations.
- `name` must be unique only within the same owner’s organization set.
- `description` is mandatory on create and remains required after updates.
- If `is_online_only=false`, `physical_address` must be present.
- If `is_online_only=true`, `physical_address` is cleared before persistence.
- `logo` and `cover_image` are optional and independently managed.

### State Transitions (Presence Mode)

```text
PhysicalPresence --(set is_online_only=true)--> OnlineOnly
OnlineOnly --(set is_online_only=false + address provided)--> PhysicalPresence
```

- Transitioning to `OnlineOnly` clears any stored physical address.
- Transitioning to `PhysicalPresence` requires a new or existing address in the same write.

## Entity: OrganizationCollectionQuery

Represents the supported query parameters for list/read operations on organizations.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `owner_scope` | enum | optional, `all` or `mine`, default `all` | Whether to list all visible organizations or only the requester’s own |
| `organization_type` | enum/null | optional | Filter by one organization category |
| `is_online_only` | boolean/null | optional | Filter by presence mode |
| `search` | string/null | optional | Case-insensitive search fragment over public organization text |
| `ordering` | string | optional, one of `name`, `-name`, `created_at`, `-created_at`, default `-created_at` | Sort order |
| `page` | integer | optional, default `1`, minimum `1` | Requested page number |
| `page_size` | integer | optional, default `20`, maximum `100` | Page size |

### Validation Rules

- Unsupported `ordering` values fall back to the default sort.
- `page_size` values above the limit are clamped to the maximum.
- `owner_scope=mine` is valid only for authenticated requesters and returns organizations owned by `request.user`.

## Entity: OrganizationBrandingCommand

Represents one logo or cover-image upload/delete action.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `organization_id` | integer | required | Target organization |
| `actor_user_id` | integer | required | User attempting the branding mutation |
| `asset_kind` | enum | required, `logo` or `cover_image` | Branding slot being changed |
| `file` | image/null | required for upload; null for delete | Uploaded branding asset |
| `message` | string | derived | Human-readable mutation outcome |

### Validation Rules

- Only the organization owner may upload, replace, or delete branding.
- Uploads must be valid image files of allowed type and size.
- Uploading a new asset replaces the previous asset in the same slot.
- Deleting a missing asset is treated as a safe no-op response.

## Entity: OrganizationSummaryProjection

Represents the list/detail payload shape returned to authenticated viewers.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | integer | required | Organization identifier |
| `owner_id` | integer | required | Owning user identifier |
| `name` | string | required | Public organization name |
| `description` | string | required | Public description |
| `organization_type` | string | required | Stored category value |
| `is_online_only` | boolean | required | Presence-mode flag |
| `physical_address` | string/null | conditional | Address text or null for online-only organizations |
| `logo_url` | string/null | optional | Absolute logo URL |
| `cover_image_url` | string/null | optional | Absolute cover-image URL |
| `created_at` | datetime | required | Creation timestamp |
| `updated_at` | datetime | required | Last modification timestamp |

### Projection Rules

- Collection payloads use the same public organization fields as detail payloads.
- No person-profile fields are embedded into organization payloads.
- Branding URLs are returned as absolute URLs when assets exist.
