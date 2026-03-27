# API Contracts: Profiles

**Base Path**: `/api/profiles/`  
**Version**: v1  
**Date**: 27 March 2026

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/me/` | Get current user's profile |
| PATCH | `/me/` | Update current user's profile |
| POST | `/me/avatar/` | Upload profile picture |
| DELETE | `/me/avatar/` | Remove profile picture |
| GET | `/{user_id}/` | Get user profile (public view) |

---

## GET /me/

Retrieve the authenticated user's profile.

### Request

```http
GET /api/profiles/me/
Authorization: Bearer <access_token>
```

### Response (200 OK)

```json
{
  "user_id": 123,
  "email": "user@example.com",
  "display_name": "John Doe",
  "bio": "Software developer and coffee enthusiast.",
  "avatar": "https://afrourban.com/media/avatars/123_abc123.jpg",
  "phone_number": "+1234567890",
  "date_of_birth": "1990-05-15",
  "preferences": {
    "notifications": {
      "email": true,
      "push": false
    },
    "theme": "dark",
    "language": "en",
    "timezone": "America/New_York"
  },
  "created_at": "2026-01-15T08:30:00Z",
  "updated_at": "2026-03-27T10:00:00Z"
}
```

### Error Responses

**401 Unauthorized**
```json
{
  "type": "https://afrourban.com/errors/not-authenticated",
  "title": "Authentication Required",
  "status": 401,
  "detail": "Authentication credentials were not provided.",
  "instance": "/api/profiles/me/"
}
```

---

## PATCH /me/

Update the authenticated user's profile.

### Request

```http
PATCH /api/profiles/me/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "display_name": "Johnny Doe",
  "bio": "Updated bio text.",
  "phone_number": "+1987654321",
  "preferences": {
    "theme": "light"
  }
}
```

**Updatable Fields**: `display_name`, `bio`, `phone_number`, `date_of_birth`, `preferences`

### Response (200 OK)

```json
{
  "user_id": 123,
  "email": "user@example.com",
  "display_name": "Johnny Doe",
  "bio": "Updated bio text.",
  "avatar": "https://afrourban.com/media/avatars/123_abc123.jpg",
  "phone_number": "+1987654321",
  "date_of_birth": "1990-05-15",
  "preferences": {
    "notifications": {
      "email": true,
      "push": false
    },
    "theme": "light",
    "language": "en",
    "timezone": "America/New_York"
  },
  "created_at": "2026-01-15T08:30:00Z",
  "updated_at": "2026-03-27T11:00:00Z"
}
```

### Error Responses

**400 Bad Request** - Validation error
```json
{
  "type": "https://afrourban.com/errors/validation-error",
  "title": "Validation Error",
  "status": 400,
  "detail": "One or more fields failed validation.",
  "instance": "/api/profiles/me/",
  "errors": {
    "display_name": ["Display name cannot exceed 100 characters."],
    "phone_number": ["Invalid phone number format."]
  }
}
```

---

## POST /me/avatar/

Upload a new profile picture.

### Request

```http
POST /api/profiles/me/avatar/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Form Data**:
- `avatar`: File (JPEG, PNG, or WebP, max 5MB)

### Response (200 OK)

```json
{
  "avatar": "https://afrourban.com/media/avatars/123_def456.jpg",
  "message": "Profile picture updated successfully."
}
```

### Error Responses

**400 Bad Request** - Invalid file
```json
{
  "type": "https://afrourban.com/errors/validation-error",
  "title": "Validation Error",
  "status": 400,
  "detail": "Invalid file upload.",
  "instance": "/api/profiles/me/avatar/",
  "errors": {
    "avatar": ["File size exceeds 5MB limit."]
  }
}
```

**400 Bad Request** - Invalid format
```json
{
  "type": "https://afrourban.com/errors/validation-error",
  "title": "Validation Error",
  "status": 400,
  "detail": "Invalid file upload.",
  "instance": "/api/profiles/me/avatar/",
  "errors": {
    "avatar": ["Unsupported file format. Use JPEG, PNG, or WebP."]
  }
}
```

---

## DELETE /me/avatar/

Remove the current profile picture.

### Request

```http
DELETE /api/profiles/me/avatar/
Authorization: Bearer <access_token>
```

### Response (204 No Content)

*Empty response body*

---

## GET /{user_id}/

Retrieve a user's public profile.

### Request

```http
GET /api/profiles/123/
Authorization: Bearer <access_token>
```

### Response (200 OK)

```json
{
  "user_id": 123,
  "display_name": "John Doe",
  "bio": "Software developer and coffee enthusiast.",
  "avatar": "https://afrourban.com/media/avatars/123_abc123.jpg",
  "created_at": "2026-01-15T08:30:00Z"
}
```

*Note: Only public fields are returned. Email, phone, preferences, etc. are hidden.*

### Error Responses

**404 Not Found**
```json
{
  "type": "https://afrourban.com/errors/not-found",
  "title": "Not Found",
  "status": 404,
  "detail": "User profile not found.",
  "instance": "/api/profiles/999/"
}
```

---

## Model Schemas

### ProfileDetailOutput

Full profile for owner view.

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | integer | User ID |
| `email` | string | User email |
| `display_name` | string | Public display name |
| `bio` | string | User biography |
| `avatar` | string (URL) | Profile picture URL |
| `phone_number` | string | Contact number |
| `date_of_birth` | string (date) | Birth date |
| `preferences` | object | User preferences |
| `created_at` | string (datetime) | Creation timestamp |
| `updated_at` | string (datetime) | Last update timestamp |

### ProfilePublicOutput

Public profile view (other users).

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | integer | User ID |
| `display_name` | string | Public display name |
| `bio` | string | User biography |
| `avatar` | string (URL) | Profile picture URL |
| `created_at` | string (datetime) | Creation timestamp |

### ProfileUpdateInput

Profile update payload.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `display_name` | string | No | Max 100 chars |
| `bio` | string | No | Max 500 chars |
| `phone_number` | string | No | Valid phone format |
| `date_of_birth` | string (date) | No | YYYY-MM-DD |
| `preferences` | object | No | Partial update merged |
