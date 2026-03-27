# Research: Custom User & Profile Management

**Feature**: 001-user-profile-apps  
**Date**: 27 March 2026  
**Purpose**: Resolve technical decisions and document best practices before implementation

## Research Areas

### 1. Django Simple JWT Configuration

**Decision**: Use djangorestframework-simplejwt with custom token claims

**Rationale**:
- Industry-standard JWT implementation for Django REST Framework
- Supports custom claims via `TokenObtainPairSerializer` subclassing
- Built-in token refresh and blacklisting support
- Active maintenance and security updates

**Best Practices**:
- Access token lifetime: 15-60 minutes (short-lived for security)
- Refresh token lifetime: 1-7 days (balance security vs UX)
- Enable refresh token rotation (`ROTATE_REFRESH_TOKENS = True`)
- Blacklist tokens on logout (`BLACKLIST_AFTER_ROTATION = True`)
- Use `HS256` algorithm for simplicity; `RS256` for multi-service architectures

**Configuration Pattern**:
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}
```

**Alternatives Considered**:
- `django-rest-auth` / `dj-rest-auth`: Higher-level but adds unnecessary complexity
- Custom JWT implementation: Violates constitution principle VI (Simplicity & Reuse)
- Session-based auth: Not suitable for API-first design

---

### 2. Private Claims for Policy Management

**Decision**: Embed user policies and permissions as private claims in JWT tokens

**Rationale**:
- Reduces database queries on every authenticated request
- Enables stateless permission checks at the API level
- Follows JWT best practice of encoding authorization context

**Private Claims Structure**:
```json
{
  "user_id": 123,
  "email": "user@example.com",
  "policies": {
    "roles": ["editor", "moderator"],
    "permissions": ["can_edit_posts", "can_moderate_comments"],
    "restrictions": {
      "max_uploads_per_day": 10,
      "allowed_regions": ["NA", "EU"]
    }
  },
  "is_staff": false,
  "is_active": true
}
```

**Implementation Approach**:
1. Create custom `TokenObtainPairSerializer` to add claims
2. Create `claims.py` module with claim extraction/validation helpers
3. Build custom DRF permissions that read from token claims
4. Cache policy computation on user model or fetch from selectors

**Trade-offs**:
- Token size increases with policy complexity (mitigate: include only essential claims)
- Policy changes require token refresh (acceptable with 30-min access token)
- Must validate claims on security-sensitive operations (hybrid approach)

**Alternatives Considered**:
- Database lookup on every request: High latency, violates performance goals
- External policy service (OPA): Over-engineered for current scale
- Permissions in session: Not compatible with stateless JWT approach

---

### 3. Custom User Model Design

**Decision**: Create `CustomUser` extending `AbstractBaseUser` with email as username

**Rationale**:
- Email-based authentication is more user-friendly than usernames
- `AbstractBaseUser` provides flexibility while keeping model thin
- Django documentation strongly recommends custom user model from project start

**Model Fields**:
- `email` (EmailField, unique, primary identifier)
- `is_active` (BooleanField, default True)
- `is_staff` (BooleanField, default False)
- `is_superuser` (BooleanField, default False)
- `date_joined` (DateTimeField, auto_now_add)
- `last_login` (DateTimeField, null, managed by Django)

**Manager Pattern**:
```python
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        # Business logic in services.py, manager just handles ORM
        ...
    
    def create_superuser(self, email, password=None, **extra_fields):
        ...
```

**HackSoftware Styleguide Compliance**:
- Model remains thin (no business logic beyond property accessors)
- User creation logic lives in `users/services.py`
- User queries live in `users/selectors.py`

**Alternatives Considered**:
- `AbstractUser` subclass: Includes unnecessary username field
- Third-party user packages: Add complexity, constitution prefers standard Django

---

### 4. Profile Model Design

**Decision**: Separate Profile model with OneToOne relationship to User

**Rationale**:
- Separates authentication concerns from user data
- Profile can be extended without touching auth model
- Follows single responsibility principle

**Model Fields**:
- `user` (OneToOneField to CustomUser, primary_key)
- `display_name` (CharField, optional)
- `bio` (TextField, optional)
- `avatar` (ImageField, optional)
- `phone_number` (CharField, optional)
- `date_of_birth` (DateField, optional)
- `preferences` (JSONField, default dict)
- `created_at` (DateTimeField, auto_now_add)
- `updated_at` (DateTimeField, auto_now)

**Auto-creation Pattern**:
Profile created automatically via signal or service when user is created.
- Prefer service-based creation (explicit) over signal (implicit)
- Constitution principle VI: explicit > implicit

**Image Handling**:
- Use Pillow for validation and processing
- Limit to JPEG, PNG, WebP formats
- Max file size: 5MB
- Store in `MEDIA_ROOT/avatars/`
- Consider thumbnail generation for display optimization

**Alternatives Considered**:
- Embed profile in User model: Violates separation of concerns
- Profile as JSONField on User: Loses database-level validation

---

### 5. Password Validation Strategy

**Decision**: Use Django's built-in password validators with custom configuration

**Rationale**:
- Django validators are well-tested and battle-hardened
- Configurable via settings without custom code
- Meets spec requirements (8+ chars, mixed characters)

**Configuration**:
```python
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
]
```

**Alternatives Considered**:
- Custom validator: Unnecessary given Django's built-in options
- Third-party packages: Over-engineering for standard requirements

---

### 6. Role and Permission Model

**Decision**: Leverage Django's built-in Group and Permission models with custom policies

**Rationale**:
- Django's permission framework is battle-tested
- Groups serve as "roles" without custom implementation
- Custom policies can be layered on top via JWT claims

**Model Structure**:
- Use Django's `auth.Group` as roles
- Use Django's `auth.Permission` for atomic permissions
- Create `Policy` model for conditional rules (stored in DB, cached in token)

**Policy Model Fields**:
- `name` (CharField, unique)
- `description` (TextField)
- `conditions` (JSONField) - e.g., `{"time_window": {"start": "09:00", "end": "17:00"}}`
- `permissions` (ManyToMany to Permission)
- `is_active` (BooleanField)

**Alternatives Considered**:
- django-rules: Good library but adds dependency for simple needs
- django-guardian: Object-level permissions not needed initially
- Custom RBAC from scratch: Violates simplicity principle

---

### 7. API Error Response Format

**Decision**: RFC 9457 Problem Details format

**Rationale**:
- Constitution mandates consistent error envelope
- Industry standard for REST API errors
- Supported by DRF exception handler customization

**Format**:
```json
{
  "type": "https://afrourban.com/errors/validation-error",
  "title": "Validation Error",
  "status": 400,
  "detail": "The email address is already in use.",
  "instance": "/api/users/register/"
}
```

**Implementation**:
Custom exception handler in `afrourban/exceptions.py`

---

### 8. Security Logging Strategy

**Decision**: Log all auth events via structlog with JSON output

**Rationale**:
- Constitution mandates structured JSON logging
- Critical for security auditing and compliance
- Enables centralized log analysis

**Events to Log**:
- `user.registered` - email, timestamp
- `user.login.success` - user_id, ip, user_agent
- `user.login.failed` - email, ip, reason
- `user.logout` - user_id, token_jti
- `user.password.reset_requested` - email
- `user.password.changed` - user_id
- `user.permissions.changed` - user_id, changes, admin_id

**Implementation**:
Create `users/logging.py` with structured event loggers.

---

## Dependencies to Add

```toml
[tool.poetry.dependencies]
djangorestframework = "^3.14"
djangorestframework-simplejwt = "^5.3"
Pillow = "^10.0"

[tool.poetry.group.dev.dependencies]
factory-boy = "^3.3"
pytest-django = "^4.5"
```

## Open Questions (Resolved)

| Question | Resolution |
|----------|------------|
| Should policies be cached in Redis? | No - JWT claims provide sufficient caching for current scale |
| Email verification required at registration? | Deferred to P2 - basic registration works without |
| Should we support social auth? | Out of scope for this feature |

## References

- [Django Simple JWT Documentation](https://django-rest-framework-simplejwt.readthedocs.io/)
- [HackSoftware Django Styleguide](https://github.com/HackSoftware/Django-Styleguide)
- [RFC 9457 - Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457)
- [Django Custom User Model](https://docs.djangoproject.com/en/5.1/topics/auth/customizing/)
