# Research: Passkey Registration & Authentication

**Feature**: 004-passkey-auth  
**Date**: 2026-03-27

## 1. WebAuthn Library Selection

### Decision: `py_webauthn`

**Rationale**: `py_webauthn` (https://github.com/duo-labs/py_webauthn) is the most mature, actively maintained Python WebAuthn library. It provides high-level helpers for both registration and authentication ceremonies and handles CBOR/COSE encoding, attestation verification, and assertion validation internally.

**Key capabilities**:
- `generate_registration_options()` → produces `PublicKeyCredentialCreationOptions`
- `verify_registration_response()` → validates attestation, returns verified credential
- `generate_authentication_options()` → produces `PublicKeyCredentialRequestOptions`
- `verify_authentication_response()` → validates assertion, returns updated sign count
- Supports discoverable credentials (resident keys) via `resident_key=ResidentKeyRequirement.REQUIRED`
- Supports `user_verification=UserVerificationRequirement.PREFERRED`
- Returns typed dataclasses — no manual CBOR parsing needed

**Alternatives considered**:
- `fido2` (Yubico): Lower-level, requires more manual plumbing. Better for custom attestation flows but overkill for standard passkey registration/authentication.
- `webauthn` (npm): Not Python — irrelevant for this backend stack.

**Version**: Latest stable (>=2.0). Install via `poetry add py_webauthn`.

## 2. WebAuthn Protocol Flow

### Registration Ceremony

1. **Client** → `POST /api/auth/passkey/register/options/` with `{ email, display_name? }`
2. **Server** generates registration options via `generate_registration_options()`:
   - Sets `rp_id` (domain), `rp_name` ("Afrourban")
   - Sets `user_id` (random bytes, NOT the DB primary key — WebAuthn spec requirement)
   - Sets `resident_key = REQUIRED` for discoverable credentials
   - Sets `user_verification = PREFERRED`
   - Includes `challenge` (random bytes, valid for 5 minutes)
   - Excludes existing credentials for the user (`exclude_credentials`)
3. **Server** stores challenge in cache/DB, returns JSON options to client
4. **Client** calls `navigator.credentials.create()` with the options
5. **Client** → `POST /api/auth/passkey/register/complete/` with attestation response
6. **Server** calls `verify_registration_response()`, creates user + credential, triggers email verification

### Authentication Ceremony (Discoverable / Username-less)

1. **Client** → `POST /api/auth/passkey/authenticate/options/` (no body required)
2. **Server** generates authentication options via `generate_authentication_options()`:
   - Sets `rp_id`
   - Sets `allow_credentials = []` (empty — allows authenticator to present discoverable credentials)
   - Sets `user_verification = PREFERRED`
   - Includes `challenge` (random bytes, valid for 5 minutes)
3. **Server** stores challenge in cache/DB, returns JSON options to client
4. **Client** calls `navigator.credentials.get()` — authenticator presents user's credentials
5. **Client** → `POST /api/auth/passkey/authenticate/complete/` with assertion response
6. **Server** looks up credential by `credential_id` from assertion, verifies signature via `verify_authentication_response()`, checks email verified, issues JWT tokens

## 3. Challenge Storage Strategy

### Decision: Django cache framework (database-backed or Redis)

**Rationale**: WebAuthn challenges are short-lived (5 minutes), need fast read/write, and are not worth a dedicated model. Django's cache framework provides TTL-based expiry natively. The existing project uses Django's default cache (can be configured to DB or Redis per environment).

**Key details**:
- Cache key format: `webauthn_challenge:{challenge_id}` where `challenge_id` is a UUID
- Cache value: JSON with `challenge` (bytes, base64-encoded), `user_email` (for registration), `ceremony_type` ("registration" | "authentication")
- TTL: 5 minutes (300 seconds), configurable via `app_settings.WEBAUTHN_CHALLENGE_TIMEOUT_SECONDS`
- Challenge is consumed (deleted) after successful verification — prevents replay

**Alternatives considered**:
- Dedicated `WebAuthnChallenge` model: Works but adds unnecessary DB writes for ephemeral data. Would need a cleanup job for expired challenges. Overkill per Principle VI (Simplicity).
- Session-based storage: Not viable — authentication options endpoint is unauthenticated, and the API is session-less (JWT-based).

**Fallback**: If a project environment has no cache configured, Django defaults to `LocMemCache` which works for development. Production should use Redis or DB cache.

## 4. Discoverable Credential (Resident Key) Requirements

### Decision: Require resident keys for all passkey credentials

**Rationale**: The spec requires username-less authentication (clarification Q1). This means the authenticator must store the credential locally (resident key) so it can present the user identity without the server specifying `allowCredentials`.

**Implementation details**:
- `generate_registration_options()` called with `resident_key=ResidentKeyRequirement.REQUIRED`
- `authenticator_selection.resident_key = "required"` in the returned options
- `allow_credentials` is empty in authentication options (server doesn't know who's authenticating)
- Credential lookup uses `credential_id` from the assertion response to find the user
- `user.id` field in registration options uses a random 64-byte value (WebAuthn `user.id` is opaque, not the DB PK)

**Implications**:
- Hardware security keys that don't support resident keys will fail registration. This is acceptable per the spec (no fallback for non-supporting devices).
- The `WebAuthnCredential` model stores a `webauthn_user_id` (the random bytes used in registration) for consistency, though lookup primarily uses `credential_id`.

## 5. User Creation for Passkey-Only Accounts

### Decision: Reuse `CustomUserManager.create_user()` with `password=None`

**Rationale**: The existing manager already supports `password=None` (sets unusable password via `set_unusable_password()`). This means passkey-only users have no password hash — they can only authenticate via passkey.

**Implementation details**:
- `passkey_user_create()` service calls `User.objects.create_user(email=email, password=None)`
- Profile is created, email verification is triggered (same as password-based registration)
- `user.has_usable_password()` returns `False` for passkey-only users — used in FR-013 (prevent removing last passkey when no password)

## 6. JWT Token Issuance for Passkey Authentication

### Decision: Reuse `RefreshToken.for_user()` from SimpleJWT

**Rationale**: The spec says "the system returns the same token format regardless of whether the user authenticated via password or passkey." `RefreshToken.for_user(user)` creates access + refresh tokens with the same claims as password authentication.

**Implementation details**:
- After successful assertion verification, call `RefreshToken.for_user(user)`
- Custom claims from `users/claims.py` are already injected via `CustomTokenObtainPairSerializer.get_token()` — but that's tied to the serializer. We need to ensure claims are also applied for passkey auth.
- **Solution**: Extract claim injection into a standalone function (already exists as `build_token_claims`) and apply it to the token obtained from `RefreshToken.for_user()`. Or, simpler: use the SIMPLE_JWT `TOKEN_OBTAIN_PAIR_SERIALIZER` signal/hook. Actually, looking at the existing code, the custom claims are added in `CustomTokenObtainPairSerializer.get_token()` which overrides `@classmethod get_token(cls, user)`. We can call this classmethod directly: `token = CustomTokenObtainPairSerializer.get_token(user)` to get a refresh token with custom claims.

## 7. Sign Count Validation and Credential Disabling

### Decision: Validate sign count in assertion verification; disable credential on cloning detection

**Rationale**: Per FR-016 and clarification Q4, if the presented sign count ≤ stored sign count, the system must reject authentication and disable the credential.

**Implementation details**:
- `py_webauthn.verify_authentication_response()` does NOT automatically reject based on sign count — it returns the new sign count for the caller to validate
- Our service must compare: `if verified_auth.new_sign_count <= credential.sign_count and verified_auth.new_sign_count != 0:`
  - Note: sign count of 0 means the authenticator doesn't support counting (valid case)
- On cloning detection:
  - Set `credential.is_enabled = False`
  - Log a security event via structlog
  - Raise `ValidationError(code="credential_cloned")`
- Recovery: User must remove the disabled credential via management endpoint, then re-add a new passkey

## 8. Relying Party Configuration

### Decision: Configure via `users/conf.py` app settings

**Rationale**: RP ID and RP name are deployment-specific. Following the project's existing pattern in `users/conf.py`, add WebAuthn settings to `_AppSettings`.

**New settings**:
- `USERS_WEBAUTHN_RP_ID`: Relying party ID (domain). Default: `"localhost"`
- `USERS_WEBAUTHN_RP_NAME`: Human-friendly RP name. Default: `"Afrourban"`
- `USERS_WEBAUTHN_ORIGIN`: Expected origin for verification. Default: `"http://localhost:8000"`
- `USERS_WEBAUTHN_CHALLENGE_TIMEOUT_SECONDS`: Challenge expiry. Default: `300` (5 minutes)
- `USERS_WEBAUTHN_MAX_CREDENTIALS_PER_USER`: Max passkeys per user. Default: `5`

## 9. Data Encoding and Serialization

### Decision: Base64URL encoding for binary WebAuthn fields

**Rationale**: WebAuthn credentials contain binary data (credential ID, public key, challenge). JSON APIs need string encoding. Base64URL (no padding) is the standard encoding used by the WebAuthn specification and `py_webauthn`.

**Implementation details**:
- `py_webauthn` provides `options_to_json()` for serializing registration/authentication options
- Attestation/assertion responses from the client arrive as Base64URL-encoded JSON
- `credential_id` and `public_key` are stored in the DB as `BinaryField` (raw bytes)
- `webauthn_user_id` is stored as `BinaryField`
- The serializer layer handles Base64URL ↔ bytes conversion at API boundaries
