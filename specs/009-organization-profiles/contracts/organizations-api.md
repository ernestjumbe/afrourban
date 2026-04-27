# Organizations API Contract

**Feature**: 009-organization-profiles  
**Date**: 2026-04-25

## 1. Namespace and Routing Contract

1. All organizations routes live under `/api/v1/organizations/`.
2. Routes are defined in `organizations.urls.api_v1_urlpatterns`.
3. Main `afrourban/urls.py` continues to include the organizations routes through `api_v1_module_urlpatterns` and `api_urlpatterns` under `/api/`.
4. OpenAPI documentation must be regenerated with drf-spectacular (OpenAPI 3.0+).

## 2. Authentication and Permission Contract

- All organizations endpoints are authenticated in v1.
- Any authenticated user may read the collection and detail endpoints.
- Only the organization owner may update organization metadata or branding.
- Validation and permission failures use the project’s RFC 9457 Problem Details error envelope.

## 3. Collection Contract

### Endpoint

- `GET /api/v1/organizations/`

### Query Parameters

| Parameter | Required | Rules |
|-----------|----------|-------|
| `owner_scope` | no | `all` or `mine`; defaults to `all` |
| `organization_type` | no | one supported organization type |
| `is_online_only` | no | `true` or `false` |
| `search` | no | case-insensitive search fragment |
| `ordering` | no | `name`, `-name`, `created_at`, `-created_at`; defaults to `-created_at` |
| `page` | no | integer >= 1; defaults to `1` |
| `page_size` | no | integer 1-100; defaults to `20` |

### Response Envelope

Collection responses use the existing pagination envelope:

| Field | Description |
|-------|-------------|
| `count` | Total matching organizations |
| `next` | Absolute URL for next page or `null` |
| `previous` | Absolute URL for previous page or `null` |
| `results` | Array of organization summary objects |

### Organization Summary Object

| Field | Description |
|-------|-------------|
| `id` | Organization id |
| `owner_id` | Owning user id |
| `name` | Public organization name |
| `description` | Public organization description |
| `organization_type` | Stored category value |
| `is_online_only` | Presence-mode flag |
| `physical_address` | Address text or `null` |
| `logo_url` | Absolute logo URL or `null` |
| `cover_image_url` | Absolute cover-image URL or `null` |
| `created_at` | Creation timestamp |
| `updated_at` | Last modification timestamp |

## 4. Create Contract

### Endpoint

- `POST /api/v1/organizations/`

### Request Body

| Field | Required | Rules |
|-------|----------|-------|
| `name` | yes | max 255 chars; unique per owner (case-insensitive) |
| `description` | yes | non-empty |
| `organization_type` | yes | supported category choice |
| `is_online_only` | yes | boolean |
| `physical_address` | conditional | required when `is_online_only=false`; omitted or blank when `is_online_only=true` |

### Behavior

- `owner` is always derived from `request.user`.
- Create requests do not accept `logo` or `cover_image`; branding is handled by dedicated endpoints.
- If the same owner already has an organization with the same name (case-insensitive), creation fails.

### Success Response

- Returns HTTP `201 Created` with the full organization detail object.

## 5. Detail and Update Contract

### Endpoints

- `GET /api/v1/organizations/{organization_id}/`
- `PATCH /api/v1/organizations/{organization_id}/`

### Detail Response

Returns the same fields as the organization summary object.

### Update Request Body

All metadata fields are optional for patch operations:

| Field | Rules |
|-------|-------|
| `name` | if supplied, must remain unique per owner (case-insensitive) |
| `description` | if supplied, must remain non-empty |
| `organization_type` | if supplied, must be a supported category |
| `is_online_only` | if `true`, stored `physical_address` is cleared |
| `physical_address` | required whenever resulting `is_online_only=false` |

### Permission Contract

- Owners may update their organizations.
- Non-owners receive HTTP `403 Forbidden` on patch attempts.

## 6. Branding Contract

### Endpoints

- `POST /api/v1/organizations/{organization_id}/logo/`
- `DELETE /api/v1/organizations/{organization_id}/logo/`
- `POST /api/v1/organizations/{organization_id}/cover/`
- `DELETE /api/v1/organizations/{organization_id}/cover/`

### Upload Request Contract

| Endpoint | Content Type | Field |
|----------|--------------|-------|
| `POST .../logo/` | `multipart/form-data` | `logo` |
| `POST .../cover/` | `multipart/form-data` | `cover_image` |

### Upload Validation

- Allowed formats: JPEG, PNG, WebP
- Maximum file size: 5MB
- Only owners may upload or replace branding

### Upload Success Contract

| Field | Description |
|-------|-------------|
| `asset_url` | Absolute URL of the uploaded asset |
| `message` | Human-readable success message |

### Delete Success Contract

- Returns HTTP `204 No Content`

## 7. Error Contract

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

- duplicate organization name for the same owner
- missing `physical_address` when `is_online_only=false`
- unsupported organization type
- non-owner metadata or branding mutation attempt
- unsupported image type or oversized upload

## 8. Documentation, Compatibility, and Deprecation

1. Public and internal schemas must include all organizations endpoints.
2. Endpoint documentation must describe filtering, pagination, sorting, and owner-only writes.
3. This is an additive `/api/v1/` feature and does not deprecate any existing route.
4. Organization deletion, ownership transfer, and anonymous public-read exposure are not part of this iteration’s API contract.
