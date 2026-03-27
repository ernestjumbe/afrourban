# Data Model: Custom User & Profile Management

**Feature**: 001-user-profile-apps  
**Date**: 27 March 2026  
**Based on**: [research.md](research.md)

## Entity Relationship Diagram

```
┌─────────────────────┐     ┌─────────────────────┐
│     CustomUser      │     │       Profile       │
├─────────────────────┤     ├─────────────────────┤
│ id (PK)             │────<│ user (PK, FK)       │
│ email (unique)      │     │ display_name        │
│ password            │     │ bio                 │
│ is_active           │     │ avatar              │
│ is_staff            │     │ phone_number        │
│ is_superuser        │     │ date_of_birth       │
│ date_joined         │     │ preferences (JSON)  │
│ last_login          │     │ created_at          │
└─────────────────────┘     │ updated_at          │
         │                  └─────────────────────┘
         │
         │ many-to-many
         ▼
┌─────────────────────┐     ┌─────────────────────┐
│       Group         │────<│    Permission       │
├─────────────────────┤     ├─────────────────────┤
│ id (PK)             │     │ id (PK)             │
│ name (unique)       │     │ codename            │
│ permissions (M2M)   │     │ name                │
└─────────────────────┘     │ content_type (FK)   │
                            └─────────────────────┘
         │
         │ many-to-many
         ▼
┌─────────────────────┐
│       Policy        │
├─────────────────────┤
│ id (PK)             │
│ name (unique)       │
│ description         │
│ conditions (JSON)   │
│ is_active           │
│ created_at          │
│ updated_at          │
└─────────────────────┘
```

## Entity Definitions

### CustomUser

The core authentication entity representing an account holder.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | BigAutoField | PK | Unique identifier |
| `email` | EmailField | unique, max_length=255 | Primary login identifier |
| `password` | CharField | max_length=128 | Hashed password (Django default) |
| `is_active` | BooleanField | default=True | Account enabled/disabled |
| `is_staff` | BooleanField | default=False | Django admin access |
| `is_superuser` | BooleanField | default=False | Full system permissions |
| `date_joined` | DateTimeField | auto_now_add | Account creation timestamp |
| `last_login` | DateTimeField | null, blank | Last successful login |
| `groups` | ManyToMany | to auth.Group | Role assignments |
| `user_permissions` | ManyToMany | to auth.Permission | Direct permission assignments |

**Validation Rules**:
- Email must be valid format and unique (case-insensitive)
- Password must pass Django validators (8+ chars, not common, not all numeric)

**State Transitions**:
```
[Created] --activate--> [Active] --deactivate--> [Inactive]
                            │
                            └──soft_delete──> [Deleted]
```

---

### Profile

Extended user information, one-to-one with CustomUser.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `user` | OneToOneField | PK, FK to CustomUser | Link to auth entity |
| `display_name` | CharField | max_length=100, blank | Public display name |
| `bio` | TextField | max_length=500, blank | Short biography |
| `avatar` | ImageField | upload_to='avatars/', blank | Profile picture |
| `phone_number` | CharField | max_length=20, blank | Contact number |
| `date_of_birth` | DateField | null, blank | Birth date |
| `preferences` | JSONField | default=dict | User settings/preferences |
| `created_at` | DateTimeField | auto_now_add | Profile creation |
| `updated_at` | DateTimeField | auto_now | Last modification |

**Validation Rules**:
- Avatar: JPEG/PNG/WebP only, max 5MB
- Phone: Optional, validated format if provided
- Display name: No special characters except spaces and hyphens

**Preferences Schema** (JSONField):
```json
{
  "notifications": {
    "email": true,
    "push": false
  },
  "theme": "light",
  "language": "en",
  "timezone": "UTC"
}
```

---

### Policy

Conditional access rules that can be assigned to groups.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | BigAutoField | PK | Unique identifier |
| `name` | CharField | unique, max_length=100 | Policy identifier |
| `description` | TextField | blank | Human-readable description |
| `conditions` | JSONField | default=dict | Rule conditions |
| `is_active` | BooleanField | default=True | Policy enabled/disabled |
| `created_at` | DateTimeField | auto_now_add | Creation timestamp |
| `updated_at` | DateTimeField | auto_now | Last modification |

**Conditions Schema** (JSONField):
```json
{
  "time_window": {
    "start": "09:00",
    "end": "17:00",
    "timezone": "UTC"
  },
  "ip_whitelist": ["192.168.1.0/24"],
  "max_requests_per_hour": 1000,
  "require_mfa": false
}
```

---

## Relationships

| From | To | Type | Description |
|------|-----|------|-------------|
| Profile | CustomUser | OneToOne | Each user has exactly one profile |
| CustomUser | Group | ManyToMany | Users can have multiple roles |
| CustomUser | Permission | ManyToMany | Direct permission grants |
| Group | Permission | ManyToMany | Roles bundle permissions |
| Group | Policy | ManyToMany (via GroupPolicy) | Roles can have policy restrictions |

---

## Indexes

```python
# CustomUser
indexes = [
    models.Index(fields=['email']),
    models.Index(fields=['is_active', 'is_staff']),
]

# Profile
indexes = [
    models.Index(fields=['display_name']),
]

# Policy
indexes = [
    models.Index(fields=['name']),
    models.Index(fields=['is_active']),
]
```

---

## JWT Token Claims Structure

When a user authenticates, the following claims are embedded in the JWT:

```json
{
  "token_type": "access",
  "exp": 1711555200,
  "iat": 1711553400,
  "jti": "unique-token-id",
  "user_id": 123,
  "email": "user@example.com",
  "is_staff": false,
  "is_active": true,
  "policies": {
    "roles": ["editor", "moderator"],
    "permissions": [
      "users.view_profile",
      "posts.add_post",
      "posts.change_post"
    ],
    "restrictions": {
      "time_window": {"start": "09:00", "end": "17:00"},
      "max_uploads_per_day": 10
    }
  }
}
```

---

## Migration Strategy

1. **Create users app first** - CustomUser model must exist before any ForeignKey references
2. **Set AUTH_USER_MODEL** - In settings before first migration
3. **Create profiles app** - After users app is stable
4. **Create policies** - Can be added incrementally

**Order of operations**:
```bash
# 1. Create users app and model
poetry run python manage.py startapp users
# Configure AUTH_USER_MODEL = 'users.CustomUser'
poetry run python manage.py makemigrations users
poetry run python manage.py migrate

# 2. Create profiles app
poetry run python manage.py startapp profiles
poetry run python manage.py makemigrations profiles
poetry run python manage.py migrate

# 3. Add Policy model to users app (or separate policies app)
poetry run python manage.py makemigrations users
poetry run python manage.py migrate
```
