# Quickstart: Custom User & Profile Management

**Feature**: 001-user-profile-apps  
**Date**: 27 March 2026

## Prerequisites

- Python 3.11+
- Poetry installed
- PostgreSQL running
- Project cloned and `poetry install` completed

## Quick Setup

### 1. Install Dependencies

```bash
# Add required packages
poetry add djangorestframework djangorestframework-simplejwt Pillow

# Add dev dependencies
poetry add --group dev factory-boy pytest-django
```

### 2. Create Django Apps

```bash
# Create the apps
poetry run python manage.py startapp users
poetry run python manage.py startapp profiles
```

### 3. Configure Settings

Add to `afrourban/settings/base.py`:

```python
INSTALLED_APPS = [
    # ... existing apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'users',
    'profiles',
]

# Custom user model (MUST be set before first migration)
AUTH_USER_MODEL = 'users.CustomUser'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'EXCEPTION_HANDLER': 'afrourban.exceptions.problem_details_exception_handler',
}

# Simple JWT settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'TOKEN_OBTAIN_SERIALIZER': 'users.serializers.CustomTokenObtainPairSerializer',
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
]
```

### 4. Run Migrations

```bash
# Create and apply migrations
poetry run python manage.py makemigrations users profiles
poetry run python manage.py migrate
```

### 5. Create Superuser

```bash
poetry run python manage.py createsuperuser
```

## Verify Setup

### Run Tests

```bash
poetry run pytest tests/users/ tests/profiles/ -v
```

### Start Dev Server

```bash
poetry run python manage.py runserver
```

### Test Authentication

```bash
# Register new user
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123!", "password_confirm": "TestPass123!"}'

# Obtain token
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123!"}'

# Access protected endpoint
curl http://127.0.0.1:8000/api/profiles/me/ \
  -H "Authorization: Bearer <access_token>"
```

## Project Structure After Setup

```
afrourban/
├── afrourban/
│   ├── settings/
│   ├── urls.py
│   └── exceptions.py     # RFC 9457 exception handler
├── users/
│   ├── models.py         # CustomUser model
│   ├── services.py       # Business logic
│   ├── selectors.py      # Query logic
│   ├── serializers.py    # DRF serializers
│   ├── views.py          # API views
│   ├── urls.py           # URL routing
│   ├── permissions.py    # Custom permissions
│   └── claims.py         # JWT claims handling
├── profiles/
│   ├── models.py         # Profile model
│   ├── services.py       # Business logic
│   ├── selectors.py      # Query logic
│   ├── serializers.py    # DRF serializers
│   ├── views.py          # API views
│   └── urls.py           # URL routing
└── tests/
    ├── factories/
    ├── users/
    └── profiles/
```

## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | POST | User registration |
| `/api/auth/token/` | POST | Login (get tokens) |
| `/api/auth/token/refresh/` | POST | Refresh access token |
| `/api/auth/logout/` | POST | Logout (blacklist token) |
| `/api/profiles/me/` | GET/PATCH | Current user profile |
| `/api/profiles/me/avatar/` | POST/DELETE | Profile picture |
| `/api/admin/users/` | GET | List users (admin) |
| `/api/admin/users/roles/` | GET/POST | Manage roles (admin) |

## Next Steps

1. Run `/speckit.tasks` to generate implementation tasks
2. Follow test-first development: write tests before implementation
3. Implement in order: users app → profiles app → admin endpoints
