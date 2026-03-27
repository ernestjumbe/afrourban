# API Contract: Age Verification

**Feature**: 002-age-verification-field  
**Date**: 27 March 2026  
**Base URL**: `/api/v1`

## Overview

This document defines the API endpoints for age verification. These extend the existing Profile endpoints from feature 001.

---

## Profile Endpoints (Extended)

### GET /api/v1/profiles/me/

Returns the authenticated user's profile with age verification data.

**Authentication**: Required (Bearer token)

**Response** (200 OK):
```json
{
  "user_id": 123,
  "display_name": "John Doe",
  "bio": "Software developer",
  "avatar": "https://example.com/avatars/123.jpg",
  "date_of_birth": "1998-05-15",
  "age": 27,
  "age_verification_status": "self_declared",
  "age_verified_at": "2026-03-27T10:30:00Z",
  "preferences": {
    "theme": "dark"
  },
  "created_at": "2026-01-15T09:00:00Z",
  "updated_at": "2026-03-27T10:30:00Z"
}
```

**Note**: `date_of_birth` is ONLY included when user views their own profile.

---

### GET /api/v1/profiles/{user_id}/

Returns a public profile (another user's profile).

**Authentication**: Required (Bearer token)

**Response** (200 OK):
```json
{
  "user_id": 456,
  "display_name": "Jane Smith",
  "bio": "Designer",
  "avatar": "https://example.com/avatars/456.jpg",
  "age": 25,
  "age_verified": true
}
```

**Note**: `date_of_birth` is NEVER included in public profiles. Only `age` and `age_verified` boolean.

---

### PATCH /api/v1/profiles/me/

Update the authenticated user's profile, including date of birth.

**Authentication**: Required (Bearer token)

**Request Body**:
```json
{
  "date_of_birth": "1998-05-15"
}
```

**Response** (200 OK):
```json
{
  "user_id": 123,
  "display_name": "John Doe",
  "date_of_birth": "1998-05-15",
  "age": 27,
  "age_verification_status": "self_declared",
  "age_verified_at": "2026-03-27T10:35:00Z"
}
```

**Validation Errors** (400 Bad Request):

Date in the future:
```json
{
  "type": "https://afrourban.com/errors/validation-error",
  "title": "Validation Error",
  "status": 400,
  "detail": "Date of birth cannot be in the future.",
  "instance": "/api/v1/profiles/me/"
}
```

Date too far in the past:
```json
{
  "type": "https://afrourban.com/errors/validation-error",
  "title": "Validation Error",
  "status": 400,
  "detail": "Date of birth cannot be more than 120 years ago.",
  "instance": "/api/v1/profiles/me/"
}
```

---

## Age Policy Endpoint

### GET /api/v1/policies/{policy_id}/check/

Check if the authenticated user passes a specific policy.

**Authentication**: Required (Bearer token)

**Response** (200 OK - passes policy):
```json
{
  "policy_id": 1,
  "policy_name": "adult_content_access",
  "passed": true,
  "evaluated_at": "2026-03-27T10:40:00Z"
}
```

**Response** (200 OK - fails policy):
```json
{
  "policy_id": 1,
  "policy_name": "adult_content_access",
  "passed": false,
  "reason": "minimum_age_not_met",
  "message": "You must be at least 18 years old to access this feature.",
  "evaluated_at": "2026-03-27T10:40:00Z"
}
```

**Response** (200 OK - age unknown):
```json
{
  "policy_id": 1,
  "policy_name": "adult_content_access",
  "passed": false,
  "reason": "age_unknown",
  "message": "Please provide your date of birth to access this feature.",
  "evaluated_at": "2026-03-27T10:40:00Z"
}
```

---

## JWT Token Claims

When user authenticates, the JWT token includes age verification data (if date of birth is provided):

**Token Payload**:
```json
{
  "token_type": "access",
  "exp": 1711534200,
  "iat": 1711532400,
  "jti": "abc123",
  "user_id": 123,
  "email": "user@example.com",
  "policies": ["can_view_dashboard"],
  "roles": ["user"],
  "age_verification": {
    "age": 27,
    "status": "self_declared",
    "verified_at": "2026-03-27T10:30:00Z"
  }
}
```

**Note**: `date_of_birth` is NEVER included in JWT tokens.

---

## Error Responses

All errors follow RFC 9457 Problem Details format:

| HTTP Status | Type | When |
|-------------|------|------|
| 400 | validation-error | Invalid date_of_birth format or value |
| 401 | unauthorized | Missing or invalid authentication |
| 403 | age-restricted | User fails minimum age policy |
| 404 | not-found | Profile or policy not found |

**Example 403 Age Restricted**:
```json
{
  "type": "https://afrourban.com/errors/age-restricted",
  "title": "Age Restricted",
  "status": 403,
  "detail": "You must be at least 18 years old to access this feature.",
  "instance": "/api/v1/features/adult-content/"
}
```
