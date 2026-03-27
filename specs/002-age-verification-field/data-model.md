# Data Model: Age Verification Field

**Feature**: 002-age-verification-field  
**Date**: 27 March 2026  
**Based on**: [research.md](research.md)
**Extends**: Feature 001 data model

## Entity Relationship Diagram

```
┌─────────────────────────────────────────┐
│           Profile (extended)            │
├─────────────────────────────────────────┤
│ user (PK, FK)                           │
│ display_name                            │
│ bio                                     │
│ avatar                                  │
│ phone_number                            │
│ date_of_birth        ← existing field   │
│ preferences (JSON)                      │
│ created_at                              │
│ updated_at                              │
│ ─────────────────────────────────────── │
│ + age_verification_status  ← NEW        │
│ + age_verified_at          ← NEW        │
│ + age                      ← COMPUTED   │
└─────────────────────────────────────────┘
          │
          │ policy evaluation
          ▼
┌─────────────────────────────────────────┐
│           Policy (extended)             │
├─────────────────────────────────────────┤
│ id (PK)                                 │
│ name (unique)                           │
│ description                             │
│ conditions (JSON)     ← extended        │
│   + minimum_age: int  ← NEW condition   │
│ is_active                               │
│ created_at                              │
│ updated_at                              │
└─────────────────────────────────────────┘
```

## Entity Definitions

### Profile (Extended)

Extends the Profile model from feature 001 with age verification fields.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `age_verification_status` | CharField | choices=AgeVerificationStatus, default="unverified" | Current verification state |
| `age_verified_at` | DateTimeField | null, blank | Timestamp of last status change |
| `age` | (computed) | read-only property | Current age in years (not stored) |

**AgeVerificationStatus Enum**:
| Value | Label | State |
|-------|-------|-------|
| `unverified` | Unverified | Active (default) |
| `self_declared` | Self Declared | Active |
| `pending` | Pending Verification | Reserved |
| `verified` | Verified | Reserved |
| `failed` | Verification Failed | Reserved |

**Validation Rules**:
- `date_of_birth`: Not in future, not more than 120 years ago
- `age_verification_status`: Must use defined enum values
- `age_verified_at`: Auto-updated when status changes

**State Transitions**:
```
[unverified] ──provide DOB──> [self_declared]
                                    │
                              update DOB
                                    │
                                    ▼
                               [self_declared] (timestamp reset)

Reserved (future):
[self_declared] ──submit docs──> [pending] ──approve──> [verified]
                                     │
                                     └──reject──> [failed]
```

**Computed Properties**:
```python
@property
def age(self) -> int | None:
    """Calculate current age from date_of_birth."""
    if not self.date_of_birth:
        return None
    today = date.today()
    age = today.year - self.date_of_birth.year
    if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
        age -= 1
    return age

@property
def age_verified(self) -> bool:
    """Check if age has been provided (at minimum self_declared)."""
    return self.age_verification_status != AgeVerificationStatus.UNVERIFIED
```

---

### Policy (Extended)

Extends the Policy model conditions schema with age-related constraints.

**Conditions Schema Extension**:
```json
{
  "minimum_age": 18,
  "time_window": {
    "start": "09:00",
    "end": "17:00"
  },
  "ip_whitelist": ["192.168.1.0/24"]
}
```

| Condition Key | Type | Description |
|---------------|------|-------------|
| `minimum_age` | integer | Minimum age in years required to pass policy |

**Policy Evaluation Logic**:
```python
def evaluate_minimum_age(profile: Profile, conditions: dict) -> bool:
    """Evaluate minimum_age condition."""
    min_age = conditions.get("minimum_age")
    if min_age is None:
        return True  # No age restriction
    
    if profile.age is None:
        return False  # Unknown age fails
    
    return profile.age >= min_age
```

---

## JWT Claims Extension

When user has provided date_of_birth, include age verification data in token:

```json
{
  "user_id": 123,
  "email": "user@example.com",
  "policies": ["can_view_dashboard"],
  "roles": ["user"],
  "age_verification": {
    "age": 25,
    "status": "self_declared",
    "verified_at": "2026-03-27T10:30:00Z"
  }
}
```

**Claim Structure**:
| Claim | Type | Description |
|-------|------|-------------|
| `age_verification.age` | integer | User's current age in years |
| `age_verification.status` | string | AgeVerificationStatus value |
| `age_verification.verified_at` | ISO8601 string | When status was last updated |

**Note**: `date_of_birth` is NEVER included in JWT claims (privacy requirement).

---

## Database Migration

```python
# profiles/migrations/000X_add_age_verification.py

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('profiles', '0001_initial'),  # From feature 001
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='age_verification_status',
            field=models.CharField(
                choices=[
                    ('unverified', 'Unverified'),
                    ('self_declared', 'Self Declared'),
                    ('pending', 'Pending Verification'),
                    ('verified', 'Verified'),
                    ('failed', 'Verification Failed'),
                ],
                default='unverified',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='profile',
            name='age_verified_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
```

---

## Indexes

| Table | Index | Columns | Purpose |
|-------|-------|---------|---------|
| profiles_profile | idx_age_verification_status | age_verification_status | Filter profiles by verification state |
