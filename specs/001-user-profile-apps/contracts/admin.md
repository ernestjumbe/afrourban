# API Contracts: User Administration

**Base Path**: `/api/admin/users/`  
**Version**: v1  
**Date**: 27 March 2026  
**Required Permission**: `users.manage_users` (staff only)

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all users |
| GET | `/{user_id}/` | Get user details |
| PATCH | `/{user_id}/` | Update user account |
| POST | `/{user_id}/activate/` | Activate user account |
| POST | `/{user_id}/deactivate/` | Deactivate user account |
| GET | `/{user_id}/permissions/` | Get user permissions |
| PUT | `/{user_id}/permissions/` | Set user permissions |
| GET | `/roles/` | List available roles |
| POST | `/roles/` | Create new role |
| GET | `/roles/{role_id}/` | Get role details |
| PATCH | `/roles/{role_id}/` | Update role |
| DELETE | `/roles/{role_id}/` | Delete role |

---

## GET /

List all users with pagination and filtering.

### Request

```http
GET /api/admin/users/?page=1&page_size=20&is_active=true&search=john
Authorization: Bearer <access_token>
```

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `page_size` | integer | 20 | Items per page (max 100) |
| `is_active` | boolean | - | Filter by active status |
| `is_staff` | boolean | - | Filter by staff status |
| `search` | string | - | Search email or display name |
| `ordering` | string | `-date_joined` | Sort field |

### Response (200 OK)

```json
{
  "count": 150,
  "next": "https://afrourban.com/api/admin/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 123,
      "email": "john@example.com",
      "display_name": "John Doe",
      "is_active": true,
      "is_staff": false,
      "date_joined": "2026-01-15T08:30:00Z",
      "last_login": "2026-03-27T09:00:00Z",
      "roles": ["editor", "moderator"]
    }
  ]
}
```

### Error Responses

**403 Forbidden** - Insufficient permissions
```json
{
  "type": "https://afrourban.com/errors/permission-denied",
  "title": "Permission Denied",
  "status": 403,
  "detail": "You do not have permission to manage users.",
  "instance": "/api/admin/users/"
}
```

---

## GET /{user_id}/

Get detailed user information.

### Request

```http
GET /api/admin/users/123/
Authorization: Bearer <access_token>
```

### Response (200 OK)

```json
{
  "id": 123,
  "email": "john@example.com",
  "is_active": true,
  "is_staff": false,
  "is_superuser": false,
  "date_joined": "2026-01-15T08:30:00Z",
  "last_login": "2026-03-27T09:00:00Z",
  "profile": {
    "display_name": "John Doe",
    "bio": "Software developer",
    "avatar": "https://afrourban.com/media/avatars/123_abc.jpg",
    "phone_number": "+1234567890"
  },
  "roles": [
    {"id": 1, "name": "editor"},
    {"id": 2, "name": "moderator"}
  ],
  "permissions": [
    "posts.add_post",
    "posts.change_post",
    "comments.delete_comment"
  ],
  "policies": [
    {"id": 1, "name": "business_hours_only"}
  ]
}
```

---

## PATCH /{user_id}/

Update user account settings.

### Request

```http
PATCH /api/admin/users/123/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "is_staff": true,
  "roles": [1, 2, 3]
}
```

**Updatable Fields**: `is_staff`, `roles` (list of role IDs)

### Response (200 OK)

```json
{
  "id": 123,
  "email": "john@example.com",
  "is_active": true,
  "is_staff": true,
  "roles": [
    {"id": 1, "name": "editor"},
    {"id": 2, "name": "moderator"},
    {"id": 3, "name": "admin"}
  ]
}
```

---

## POST /{user_id}/activate/

Activate a deactivated user account.

### Request

```http
POST /api/admin/users/123/activate/
Authorization: Bearer <access_token>
```

### Response (200 OK)

```json
{
  "id": 123,
  "email": "john@example.com",
  "is_active": true,
  "message": "User account activated successfully."
}
```

---

## POST /{user_id}/deactivate/

Deactivate a user account.

### Request

```http
POST /api/admin/users/123/deactivate/
Authorization: Bearer <access_token>
```

### Response (200 OK)

```json
{
  "id": 123,
  "email": "john@example.com",
  "is_active": false,
  "message": "User account deactivated successfully."
}
```

### Error Responses

**400 Bad Request** - Self-deactivation attempt
```json
{
  "type": "https://afrourban.com/errors/invalid-operation",
  "title": "Invalid Operation",
  "status": 400,
  "detail": "You cannot deactivate your own account.",
  "instance": "/api/admin/users/123/deactivate/"
}
```

---

## GET /{user_id}/permissions/

Get user's effective permissions (direct + via roles).

### Request

```http
GET /api/admin/users/123/permissions/
Authorization: Bearer <access_token>
```

### Response (200 OK)

```json
{
  "user_id": 123,
  "direct_permissions": [
    {"id": 10, "codename": "special_feature", "name": "Can use special feature"}
  ],
  "role_permissions": [
    {
      "role": {"id": 1, "name": "editor"},
      "permissions": [
        {"id": 1, "codename": "add_post", "name": "Can add post"},
        {"id": 2, "codename": "change_post", "name": "Can change post"}
      ]
    }
  ],
  "effective_permissions": [
    "special_feature",
    "add_post",
    "change_post"
  ]
}
```

---

## PUT /{user_id}/permissions/

Set user's direct permissions (replaces existing).

### Request

```http
PUT /api/admin/users/123/permissions/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "permission_ids": [10, 15, 20]
}
```

### Response (200 OK)

```json
{
  "user_id": 123,
  "direct_permissions": [
    {"id": 10, "codename": "special_feature"},
    {"id": 15, "codename": "view_reports"},
    {"id": 20, "codename": "export_data"}
  ],
  "message": "Permissions updated successfully."
}
```

---

## GET /roles/

List all available roles.

### Request

```http
GET /api/admin/users/roles/
Authorization: Bearer <access_token>
```

### Response (200 OK)

```json
{
  "results": [
    {
      "id": 1,
      "name": "editor",
      "user_count": 25,
      "permission_count": 5
    },
    {
      "id": 2,
      "name": "moderator",
      "user_count": 10,
      "permission_count": 8
    },
    {
      "id": 3,
      "name": "admin",
      "user_count": 3,
      "permission_count": 15
    }
  ]
}
```

---

## POST /roles/

Create a new role.

### Request

```http
POST /api/admin/users/roles/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "name": "reviewer",
  "permission_ids": [1, 2, 5, 8]
}
```

### Response (201 Created)

```json
{
  "id": 4,
  "name": "reviewer",
  "permissions": [
    {"id": 1, "codename": "view_post"},
    {"id": 2, "codename": "add_comment"},
    {"id": 5, "codename": "approve_post"},
    {"id": 8, "codename": "reject_post"}
  ]
}
```

---

## GET /roles/{role_id}/

Get role details including assigned permissions.

### Request

```http
GET /api/admin/users/roles/1/
Authorization: Bearer <access_token>
```

### Response (200 OK)

```json
{
  "id": 1,
  "name": "editor",
  "permissions": [
    {"id": 1, "codename": "add_post", "name": "Can add post"},
    {"id": 2, "codename": "change_post", "name": "Can change post"},
    {"id": 3, "codename": "delete_post", "name": "Can delete post"}
  ],
  "policies": [
    {"id": 1, "name": "business_hours_only", "is_active": true}
  ],
  "user_count": 25
}
```

---

## PATCH /roles/{role_id}/

Update a role's name or permissions.

### Request

```http
PATCH /api/admin/users/roles/1/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "name": "senior_editor",
  "permission_ids": [1, 2, 3, 4, 5]
}
```

### Response (200 OK)

```json
{
  "id": 1,
  "name": "senior_editor",
  "permissions": [
    {"id": 1, "codename": "add_post"},
    {"id": 2, "codename": "change_post"},
    {"id": 3, "codename": "delete_post"},
    {"id": 4, "codename": "publish_post"},
    {"id": 5, "codename": "feature_post"}
  ]
}
```

---

## DELETE /roles/{role_id}/

Delete a role. Users assigned to this role lose its permissions.

### Request

```http
DELETE /api/admin/users/roles/1/
Authorization: Bearer <access_token>
```

### Response (204 No Content)

*Empty response body*

### Error Responses

**400 Bad Request** - Role in use
```json
{
  "type": "https://afrourban.com/errors/invalid-operation",
  "title": "Invalid Operation",
  "status": 400,
  "detail": "Cannot delete role with assigned users. Remove users first or force delete.",
  "instance": "/api/admin/users/roles/1/"
}
```

---

## Common Error Responses

### 403 Forbidden - Insufficient Permissions

```json
{
  "type": "https://afrourban.com/errors/permission-denied",
  "title": "Permission Denied",
  "status": 403,
  "detail": "You do not have permission to perform this action.",
  "instance": "/api/admin/users/..."
}
```

### 404 Not Found

```json
{
  "type": "https://afrourban.com/errors/not-found",
  "title": "Not Found",
  "status": 404,
  "detail": "User not found.",
  "instance": "/api/admin/users/999/"
}
```
