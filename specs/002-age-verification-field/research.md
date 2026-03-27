# Research: Age Verification Field

**Feature**: 002-age-verification-field  
**Date**: 27 March 2026  
**Purpose**: Document technical decisions for age verification infrastructure

## Research Areas

### 1. Age Calculation from Date of Birth

**Decision**: Calculate age dynamically using Python's datetime, not stored in database.

**Implementation**:
```python
from datetime import date

def calculate_age(date_of_birth: date) -> int:
    """Calculate age in completed years from date of birth."""
    today = date.today()
    age = today.year - date_of_birth.year
    # Adjust if birthday hasn't occurred this year
    if (today.month, today.day) < (date_of_birth.month, date_of_birth.day):
        age -= 1
    return age
```

**Rationale**:
- Dynamic calculation always reflects current age (no stale data)
- Handles leap years correctly (Feb 29 birthdays)
- No need for scheduled jobs to update ages
- Meets SC-002 (accurate to the day)

**Alternatives considered**:
- Store age as field: Rejected (stale data, requires nightly updates)
- Use dateutil.relativedelta: Rejected (adds dependency for simple calculation)

---

### 2. Age Verification Status Enum

**Decision**: Use Django TextChoices with all values defined, but only implement active transitions.

**Implementation**:
```python
class AgeVerificationStatus(models.TextChoices):
    UNVERIFIED = "unverified", "Unverified"
    SELF_DECLARED = "self_declared", "Self Declared"
    # Reserved for future document verification
    PENDING = "pending", "Pending Verification"
    VERIFIED = "verified", "Verified"
    FAILED = "failed", "Verification Failed"
```

**Active transitions** (this feature):
- `unverified` → `self_declared` (when user provides date_of_birth)
- `self_declared` → `self_declared` (when user updates date_of_birth, timestamp resets)

**Reserved transitions** (future feature):
- `self_declared` → `pending` (when user submits documents)
- `pending` → `verified` (when documents approved)
- `pending` → `failed` (when documents rejected)

**Rationale**:
- TextChoices provides type safety and admin integration
- Defining all values upfront avoids future migration for enum changes
- Clear documentation distinguishes active vs reserved states

---

### 3. Date of Birth Validation

**Decision**: Use Django validators for boundary checks.

**Implementation**:
```python
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import date, timedelta

def max_date_of_birth():
    """Date of birth cannot be in the future."""
    return date.today()

def min_date_of_birth():
    """Date of birth cannot be more than 120 years ago."""
    return date.today() - timedelta(days=120 * 365)  # Approximate

# On model field:
date_of_birth = models.DateField(
    null=True,
    blank=True,
    validators=[
        MaxValueValidator(limit_value=max_date_of_birth),
        MinValueValidator(limit_value=min_date_of_birth),
    ]
)
```

**Rationale**:
- Callable validators ensure dynamic date checking
- 120-year limit is reasonable maximum human lifespan
- Null/blank allows optional field per FR-001

---

### 4. JWT Claims for Age Data

**Decision**: Include age and verification status in JWT, never date_of_birth.

**Claim structure**:
```json
{
  "user_id": 123,
  "email": "user@example.com",
  "policies": ["..."],
  "age_verification": {
    "age": 25,
    "status": "self_declared",
    "verified_at": "2026-03-27T10:30:00Z"
  }
}
```

**Implementation** (extend CustomTokenObtainPairSerializer):
```python
@classmethod
def get_token(cls, user):
    token = super().get_token(user)
    # ... existing claims ...
    
    profile = user.profile
    if profile.date_of_birth:
        token["age_verification"] = {
            "age": profile.age,  # computed property
            "status": profile.age_verification_status,
            "verified_at": profile.age_verified_at.isoformat() if profile.age_verified_at else None,
        }
    return token
```

**Rationale**:
- Age is sufficient for policy checks (minimum_age comparison)
- Meets FR-013 (date_of_birth not exposed)
- Enables stateless policy enforcement at API gateway level

---

### 5. Minimum Age Policy Condition

**Decision**: Extend existing Policy.conditions JSONField with `minimum_age` key.

**Conditions schema extension**:
```json
{
  "minimum_age": 18,
  "time_window": {...},
  "ip_whitelist": [...]
}
```

**Evaluation logic** (in policy service):
```python
def evaluate_age_condition(user_profile: Profile, min_age: int) -> bool:
    """Check if user meets minimum age requirement."""
    if not user_profile.date_of_birth:
        return False  # Unknown age fails
    return user_profile.age >= min_age
```

**Rationale**:
- Leverages existing Policy model from feature 001
- JSON conditions are already extensible by design
- Simple integer comparison for age check

---

### 6. Privacy Compliance

**Decision**: Never expose date_of_birth in public API responses.

**Output serializer**:
```python
class ProfilePublicSerializer(serializers.Serializer):
    """Public profile data - no sensitive fields."""
    display_name = serializers.CharField()
    avatar = serializers.ImageField()
    age = serializers.IntegerField(source="age", read_only=True)
    age_verified = serializers.BooleanField(read_only=True)
    
    # Explicitly exclude: date_of_birth, phone_number, etc.

class ProfilePrivateSerializer(ProfilePublicSerializer):
    """Private profile data - for user's own profile only."""
    date_of_birth = serializers.DateField(allow_null=True)
    # ... other sensitive fields
```

**Rationale**:
- Meets FR-012 and FR-013 (privacy requirements)
- age_verified boolean is sufficient for most UI purposes
- User can see their own date_of_birth via private serializer

---

## Dependencies

No new dependencies required. Feature uses:
- Django DateField, TextChoices (built-in)
- Python datetime (standard library)
- Existing djangorestframework-simplejwt (from feature 001)

## Open Items

None — all clarifications resolved in spec.
