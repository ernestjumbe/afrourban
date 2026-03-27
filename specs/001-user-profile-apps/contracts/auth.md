# API Contracts: Authentication

**Base Path**: `/api/auth/`  
**Version**: v1  
**Date**: 27 March 2026

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register/` | Create new user account |
| POST | `/token/` | Obtain JWT token pair |
| POST | `/token/refresh/` | Refresh access token |
| POST | `/token/verify/` | Verify token validity |
| POST | `/logout/` | Blacklist refresh token |
| POST | `/password/reset/` | Request password reset |
| POST | `/password/reset/confirm/` | Complete password reset |
| POST | `/password/change/` | Change password (authenticated) |

---

## POST /register/

Create a new user account with associated profile.

### Request

```http
POST /api/auth/register/
Content-Type: application/json
```

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "display_name": "John Doe"
}
```

**Required Fields**: `email`, `password`, `password_confirm`  
**Optional Fields**: `display_name`

### Response (201 Created)

```json
{
  "id": 123,
  "email": "user@example.com",
  "profile": {
    "display_name": "John Doe",
    "avatar": null
  },
  "created_at": "2026-03-27T10:30:00Z"
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
  "instance": "/api/auth/register/",
  "errors": {
    "email": ["This email is already in use."],
    "password": ["Password must be at least 8 characters."]
  }
}
```

---

## POST /token/

Obtain JWT access and refresh tokens.

### Request

```http
POST /api/auth/token/
Content-Type: application/json
```

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

### Response (200 OK)

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 123,
    "email": "user@example.com",
    "is_staff": false,
    "policies": {
      "roles": ["member"],
      "permissions": ["profiles.view_profile", "profiles.change_profile"]
    }
  }
}
```

### Error Responses

**401 Unauthorized** - Invalid credentials
```json
{
  "type": "https://afrourban.com/errors/authentication-failed",
  "title": "Authentication Failed",
  "status": 401,
  "detail": "No active account found with the given credentials.",
  "instance": "/api/auth/token/"
}
```

**401 Unauthorized** - Account inactive
```json
{
  "type": "https://afrourban.com/errors/account-inactive",
  "title": "Account Inactive",
  "status": 401,
  "detail": "This account has been deactivated.",
  "instance": "/api/auth/token/"
}
```

---

## POST /token/refresh/

Refresh an expired access token.

### Request

```http
POST /api/auth/token/refresh/
Content-Type: application/json
```

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Response (200 OK)

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

*Note: New refresh token issued due to rotation setting.*

### Error Responses

**401 Unauthorized** - Invalid or expired token
```json
{
  "type": "https://afrourban.com/errors/token-invalid",
  "title": "Token Invalid",
  "status": 401,
  "detail": "Token is invalid or expired.",
  "instance": "/api/auth/token/refresh/"
}
```

---

## POST /token/verify/

Verify that a token is valid.

### Request

```http
POST /api/auth/token/verify/
Content-Type: application/json
```

```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Response (200 OK)

```json
{}
```

### Error Responses

**401 Unauthorized** - Invalid token
```json
{
  "type": "https://afrourban.com/errors/token-invalid",
  "title": "Token Invalid",
  "status": 401,
  "detail": "Token is invalid or expired.",
  "instance": "/api/auth/token/verify/"
}
```

---

## POST /logout/

Blacklist the refresh token to log out.

### Request

```http
POST /api/auth/logout/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Response (205 Reset Content)

```json
{}
```

### Error Responses

**401 Unauthorized** - Not authenticated
```json
{
  "type": "https://afrourban.com/errors/not-authenticated",
  "title": "Authentication Required",
  "status": 401,
  "detail": "Authentication credentials were not provided.",
  "instance": "/api/auth/logout/"
}
```

---

## POST /password/reset/

Request a password reset link via email.

### Request

```http
POST /api/auth/password/reset/
Content-Type: application/json
```

```json
{
  "email": "user@example.com"
}
```

### Response (200 OK)

*Always returns success to prevent email enumeration.*

```json
{
  "detail": "If an account exists with this email, a password reset link has been sent."
}
```

---

## POST /password/reset/confirm/

Complete password reset with token from email.

### Request

```http
POST /api/auth/password/reset/confirm/
Content-Type: application/json
```

```json
{
  "token": "reset-token-from-email",
  "password": "NewSecurePass123!",
  "password_confirm": "NewSecurePass123!"
}
```

### Response (200 OK)

```json
{
  "detail": "Password has been reset successfully."
}
```

### Error Responses

**400 Bad Request** - Invalid token
```json
{
  "type": "https://afrourban.com/errors/invalid-token",
  "title": "Invalid Token",
  "status": 400,
  "detail": "The password reset token is invalid or has expired.",
  "instance": "/api/auth/password/reset/confirm/"
}
```

---

## POST /password/change/

Change password for authenticated user.

### Request

```http
POST /api/auth/password/change/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "old_password": "CurrentPass123!",
  "new_password": "NewSecurePass456!",
  "new_password_confirm": "NewSecurePass456!"
}
```

### Response (200 OK)

```json
{
  "detail": "Password has been changed successfully."
}
```

### Error Responses

**400 Bad Request** - Invalid old password
```json
{
  "type": "https://afrourban.com/errors/validation-error",
  "title": "Validation Error",
  "status": 400,
  "detail": "Current password is incorrect.",
  "instance": "/api/auth/password/change/"
}
```

---

## JWT Token Structure

### Access Token Claims

```json
{
  "token_type": "access",
  "exp": 1711555200,
  "iat": 1711553400,
  "jti": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_id": 123,
  "email": "user@example.com",
  "is_staff": false,
  "is_active": true,
  "policies": {
    "roles": ["editor", "moderator"],
    "permissions": [
      "profiles.view_profile",
      "profiles.change_profile",
      "posts.add_post"
    ],
    "restrictions": {
      "time_window": {
        "start": "09:00",
        "end": "17:00"
      }
    }
  }
}
```

### Refresh Token Claims

```json
{
  "token_type": "refresh",
  "exp": 1711639800,
  "iat": 1711553400,
  "jti": "f1e2d3c4-b5a6-7890-dcba-fe0987654321",
  "user_id": 123
}
```
