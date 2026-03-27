# Quickstart: Age Verification Field

**Feature**: 002-age-verification-field  
**Prerequisites**: Feature 001 (user-profile-apps) must be implemented first

---

## 1. Add New Fields

After implementing feature 001, run the migration for age verification fields:

```bash
# Create migration for new Profile fields
python manage.py makemigrations profiles --name add_age_verification_fields

# Apply migration
python manage.py migrate profiles
```

---

## 2. Verify Database Changes

Check the Profile table has new columns:

```bash
python manage.py dbshell
```

```sql
\d profiles_profile;
-- Should show:
--   age_verification_status  varchar(20) default 'unverified'
--   age_verified_at          timestamp with time zone NULL
```

---

## 3. Test Age Calculation

```bash
python manage.py shell
```

```python
from profiles.models import Profile
from datetime import date

# Get a profile
profile = Profile.objects.first()

# Set date of birth
profile.date_of_birth = date(1998, 5, 15)
profile.save()

# Check computed age
print(f"Age: {profile.age}")  # Should output calculated age

# Verify status was updated
print(f"Status: {profile.age_verification_status}")  # self_declared
print(f"Verified at: {profile.age_verified_at}")     # timestamp
```

---

## 4. Test API Endpoints

### Update Profile with DOB

```bash
# Authenticate first
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}' | jq -r '.access')

# Update date of birth
curl -X PATCH http://localhost:8000/api/v1/profiles/me/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"date_of_birth": "1998-05-15"}'
```

### Verify JWT Contains Age Data

```bash
# Get new token after setting DOB
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}' | jq -r '.access')

# Decode JWT payload (base64)
echo $TOKEN | cut -d'.' -f2 | base64 -d 2>/dev/null | jq .
# Should include age_verification object with age (not date_of_birth)
```

---

## 5. Test Age-Based Policy

```python
from profiles.models import Profile
from policies.services import PolicyService

profile = Profile.objects.get(user__email="test@example.com")

# Create an age-restricted policy (18+)
policy = Policy.objects.create(
    name="adult_content_access",
    conditions={"minimum_age": 18}
)

# Check if user passes
result = PolicyService.evaluate_policy(policy, profile)
print(f"Passes 18+ policy: {result}")  # True if age >= 18
```

---

## 6. Validation Tests

Test validation rules:

```bash
# Should fail - date in future
curl -X PATCH http://localhost:8000/api/v1/profiles/me/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"date_of_birth": "2030-01-01"}'

# Should fail - too far in past
curl -X PATCH http://localhost:8000/api/v1/profiles/me/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"date_of_birth": "1800-01-01"}'
```

---

## 7. Run Tests

```bash
# Run age verification specific tests
pytest profiles/tests/test_age_verification.py -v

# Run all profile tests
pytest profiles/ -v
```

---

## Success Criteria Checklist

- [ ] Profile model has `age_verification_status` field with default "unverified"
- [ ] Profile model has `age_verified_at` timestamp field
- [ ] Profile `age` property calculates correctly from `date_of_birth`
- [ ] Setting `date_of_birth` updates status to "self_declared" and sets timestamp
- [ ] JWT tokens include `age_verification` object with `age` (never DOB)
- [ ] Public profile responses show `age` but never `date_of_birth`
- [ ] Policy evaluation checks `minimum_age` condition correctly
- [ ] Validation rejects future dates and dates > 120 years ago
