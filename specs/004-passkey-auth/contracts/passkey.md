# Passkey API Contract

**Feature**: 004-passkey-auth  
**Date**: 2026-03-27  
**Base Path**: `/api/auth/passkey/`

All endpoints follow RFC 9457 Problem Details for error responses.

---

## 1. Passkey Registration Options

**`POST /api/auth/passkey/register/options/`**

Initiates the passkey registration ceremony by returning WebAuthn creation options.

**Authentication**: None (AllowAny)

### Request Body

```json
{
  "email": "user@example.com",
  "display_name": "Jane Doe"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string (email) | Yes | Email address for the new account |
| `display_name` | string | No | Optional display name (max 100 chars) |

### Success Response — `200 OK`

```json
{
  "challenge_id": "a1b2c3d4-...",
  "options": {
    "rp": { "name": "Afrourban", "id": "example.com" },
    "user": { "id": "<base64url>", "name": "user@example.com", "displayName": "Jane Doe" },
    "challenge": "<base64url>",
    "pubKeyCredParams": [...],
    "timeout": 300000,
    "excludeCredentials": [...],
    "authenticatorSelection": {
      "residentKey": "required",
      "userVerification": "preferred"
    },
    "attestation": "none"
  }
}
```

### Error Responses

| Status | Code | Condition |
|--------|------|-----------|
| 400 | `validation_error` | Invalid email format or missing field |
| 409 | `email_already_verified` | Email belongs to a verified account |

---

## 2. Passkey Registration Complete

**`POST /api/auth/passkey/register/complete/`**

Completes the passkey registration ceremony. Creates user account and triggers email verification.

**Authentication**: None (AllowAny)

### Request Body

```json
{
  "challenge_id": "a1b2c3d4-...",
  "credential": {
    "id": "<base64url>",
    "rawId": "<base64url>",
    "response": {
      "clientDataJSON": "<base64url>",
      "attestationObject": "<base64url>"
    },
    "type": "public-key",
    "authenticatorAttachment": "platform"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `challenge_id` | string (UUID) | Yes | Challenge ID from options response |
| `credential` | object | Yes | WebAuthn attestation response from `navigator.credentials.create()` |

### Success Response — `201 Created`

```json
{
  "id": 42,
  "email": "user@example.com",
  "is_email_verified": false,
  "message": "Account created. Please verify your email address."
}
```

### Error Responses

| Status | Code | Condition |
|--------|------|-----------|
| 400 | `validation_error` | Invalid or malformed credential |
| 400 | `challenge_expired` | Challenge has expired (>5 min) |
| 400 | `challenge_invalid` | Challenge ID not found |
| 409 | `email_already_verified` | Email belongs to a verified account |

---

## 3. Passkey Authentication Options

**`POST /api/auth/passkey/authenticate/options/`**

Initiates the passkey authentication ceremony. No user identification required (discoverable credentials).

**Authentication**: None (AllowAny)

### Request Body

Empty or `{}`.

### Success Response — `200 OK`

```json
{
  "challenge_id": "e5f6a7b8-...",
  "options": {
    "challenge": "<base64url>",
    "timeout": 300000,
    "rpId": "example.com",
    "allowCredentials": [],
    "userVerification": "preferred"
  }
}
```

---

## 4. Passkey Authentication Complete

**`POST /api/auth/passkey/authenticate/complete/`**

Completes the passkey authentication ceremony. Returns JWT tokens if successful.

**Authentication**: None (AllowAny)

### Request Body

```json
{
  "challenge_id": "e5f6a7b8-...",
  "credential": {
    "id": "<base64url>",
    "rawId": "<base64url>",
    "response": {
      "clientDataJSON": "<base64url>",
      "authenticatorData": "<base64url>",
      "signature": "<base64url>",
      "userHandle": "<base64url>"
    },
    "type": "public-key"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `challenge_id` | string (UUID) | Yes | Challenge ID from options response |
| `credential` | object | Yes | WebAuthn assertion response from `navigator.credentials.get()` |

### Success Response — `200 OK`

```json
{
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>"
}
```

### Error Responses

| Status | Code | Condition |
|--------|------|-----------|
| 400 | `challenge_expired` | Challenge has expired |
| 400 | `challenge_invalid` | Challenge ID not found |
| 400 | `validation_error` | Invalid or malformed credential |
| 401 | `credential_not_found` | Credential ID not registered |
| 401 | `credential_disabled` | Credential is disabled (e.g., cloning detected) |
| 401 | `credential_cloned` | Sign count violation — credential disabled |
| 403 | `email_not_verified` | User's email is not verified |

---

## 5. Add Passkey to Existing Account

**`POST /api/auth/passkey/add/options/`**

Initiates passkey addition for an authenticated user.

**Authentication**: Required (IsAuthenticated)

### Request Body

```json
{
  "device_label": "My MacBook"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `device_label` | string | No | Label for the new passkey (max 100 chars) |

### Success Response — `200 OK`

```json
{
  "challenge_id": "c9d0e1f2-...",
  "options": { ... }
}
```

Same `options` structure as registration options (section 1), with `excludeCredentials` listing the user's existing credential IDs.

### Error Responses

| Status | Code | Condition |
|--------|------|-----------|
| 403 | `email_not_verified` | User's email is not verified |
| 409 | `max_credentials_reached` | User already has 5 passkeys |

---

**`POST /api/auth/passkey/add/complete/`**

Completes passkey addition for an authenticated user.

**Authentication**: Required (IsAuthenticated)

### Request Body

Same structure as registration complete (section 2).

### Success Response — `201 Created`

```json
{
  "id": 3,
  "device_label": "My MacBook",
  "created_at": "2026-03-27T10:30:00Z",
  "is_enabled": true
}
```

### Error Responses

| Status | Code | Condition |
|--------|------|-----------|
| 400 | `challenge_expired` | Challenge has expired |
| 400 | `challenge_invalid` | Challenge ID not found |
| 400 | `validation_error` | Invalid credential response |
| 403 | `email_not_verified` | User's email is not verified |
| 409 | `max_credentials_reached` | User already has 5 passkeys |

---

## 6. List Passkeys

**`GET /api/auth/passkey/`**

Returns the authenticated user's registered passkeys.

**Authentication**: Required (IsAuthenticated)

### Success Response — `200 OK`

```json
{
  "results": [
    {
      "id": 1,
      "device_label": "iPhone 15",
      "created_at": "2026-03-20T08:00:00Z",
      "is_enabled": true
    },
    {
      "id": 2,
      "device_label": "MacBook Pro",
      "created_at": "2026-03-25T14:30:00Z",
      "is_enabled": true
    }
  ],
  "count": 2
}
```

---

## 7. Remove Passkey

**`DELETE /api/auth/passkey/{credential_id}/`**

Removes a passkey credential from the authenticated user's account.

**Authentication**: Required (IsAuthenticated)

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `credential_id` | integer | Database ID of the credential to remove |

### Success Response — `204 No Content`

### Error Responses

| Status | Code | Condition |
|--------|------|-----------|
| 404 | `not_found` | Credential does not exist or doesn't belong to user |
| 409 | `last_auth_method` | Cannot remove last passkey when user has no password |
