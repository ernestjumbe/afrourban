# Research: Email Verification for User Registration

**Branch**: `003-email-verification-registration`  
**Phase**: 0 — Resolve all NEEDS CLARIFICATION items before design

---

## 1. Token Generation Strategy

**Decision**: `secrets.token_urlsafe(32)` — 32-byte URL-safe base64-encoded random string (43 characters)  
**Rationale**: `secrets` is the Python standard library module explicitly designed for security-sensitive tokens (PEP 506). `token_urlsafe(32)` produces 256 bits of entropy, well above the recommended minimum. It is URL-safe without additional encoding, compatible with query parameter placement, and requires no extra dependencies.  
**Alternatives considered**:
- `uuid.uuid4()` — only 122 bits of entropy; not designed for security use; UUID format leaks structural information
- `hashlib.sha256(os.urandom(32))` — functionally equivalent but lower-level and more verbose than the `secrets` module, which exists precisely to abstract this

---

## 2. Configurable App Settings Pattern

**Decision**: `getattr(django.conf.settings, 'USERS_<KEY>', DEFAULT)` accessed through a `users/conf.py` module that defines a `app_settings` object  
**Rationale**: This is the established Django third-party app pattern (used by DRF, Simple JWT, etc.). A `conf.py` module centralises all defaults, provides a single access path, and allows project settings to override any key without modifying app code. It satisfies FR-013 without requiring a new dependency.  
**Implementation pattern**:
```python
# users/conf.py
from django.conf import settings

class _AppSettings:
    @property
    def EMAIL_VERIFICATION_TOKEN_EXPIRY_DAYS(self) -> int:
        return getattr(settings, "USERS_EMAIL_VERIFICATION_TOKEN_EXPIRY_DAYS", 7)

    @property
    def EMAIL_VERIFICATION_BASE_URL(self) -> str:
        return getattr(settings, "USERS_EMAIL_VERIFICATION_BASE_URL", "")

    @property
    def EMAIL_VERIFICATION_FROM_EMAIL(self) -> str:
        return getattr(settings, "USERS_EMAIL_VERIFICATION_FROM_EMAIL", settings.DEFAULT_FROM_EMAIL)

app_settings = _AppSettings()
```
**Alternatives considered**:
- `django-appconf` — adds a dependency for a simple problem; not warranted per Principle VI (Simplicity)
- Hardcoded constants — violates FR-013 (must be overridable)

---

## 3. Email Template Rendering with `send_mail`

**Decision**: `django.template.loader.render_to_string` to render both HTML and text templates; `django.core.mail.send_mail` with `html_message` parameter for dual-format dispatch  
**Rationale**: `render_to_string` is the standard Django approach for rendering templates to strings outside a request cycle. With `APP_DIRS: True` (already set in `base.py`), templates under `users/templates/` are discovered automatically. `send_mail` accepts both `message` (plain text) and `html_message` (HTML), sending a `multipart/alternative` email.  
**Template context variables passed**:
- `user` — the recipient user instance (for personalisation)
- `verification_url` — the full verification link including token
- `base_url` — the configured base URL
- `expiry_days` — token expiry in days (for human-readable message)
- `site_name` — from `USERS_EMAIL_VERIFICATION_SITE_NAME` setting (default: "Afrourban")

**Template locations** (APP_DIRS convention):
```
users/templates/users/emails/email_verification.html
users/templates/users/emails/email_verification.txt
```
**Alternatives considered**:
- `EmailMultiAlternatives` directly — lower-level; `send_mail` with `html_message` accomplishes the same outcome with less boilerplate
- Celery async email dispatch — not in scope; infrastructure concern, not a feature requirement

---

## 4. Login Gate: Blocking Unverified Users

**Decision**: Override `CustomTokenObtainPairSerializer.validate()` to check `user.is_email_verified` before calling `super().validate()` (or after, by inspecting the internally set `self.user`). Raise `rest_framework.exceptions.AuthenticationFailed` with a distinct error code if not verified.  
**Rationale**: `TokenObtainPairSerializer.validate()` raises `AuthenticationFailed` for invalid credentials via the internal `authenticate()` call. Inserting the verification check at the same layer keeps the error type consistent and ensures the check happens before tokens are issued. The error must be distinct from a bad-password error (FR-009), so a custom `detail` string plus a custom `code` in the exception is used.  
**Implementation**:
```python
def validate(self, attrs):
    data = super().validate(attrs)
    if not self.user.is_email_verified:
        raise AuthenticationFailed(
            detail="Email address has not been verified.",
            code="email_not_verified",
        )
    return data
```
The RFC 9457 exception handler in `afrourban/exceptions.py` will surface this as a Problem Details response with `status: 401` and a `code` field.
**Alternatives considered**:
- Custom DRF authentication backend — too heavy; this is presentation-layer gating, not an auth-protocol change
- `is_active = False` until verified — conflates two separate concepts (active account vs. verified email); would break admin-managed deactivation semantics

---

## 5. Superseding Unverified Accounts on Re-Registration

**Decision**: Modify `users/services.py:user_create()` to detect an existing unverified user at the given email address, delete that user (which cascades to their `EmailVerificationToken`), then create the new user normally.  
**Rationale**: Handling in the service layer (not the serializer) keeps atomic transaction semantics — the delete and create happen in a single `@transaction.atomic` block. The serializer is updated to permit duplicate emails when the existing account is unverified, deferring the supersede logic to the service. This prevents a TOCTOU race (the `exists()` check in the serializer and the service operation are no longer separate transactions for the unverified case).  
**Modified serializer logic**:
```python
def validate_email(self, value):
    email = value.lower()
    existing = User.objects.filter(email__iexact=email).first()
    if existing and existing.is_email_verified:
        raise serializers.ValidationError("This email is already in use.")
    # Unverified or non-existent: allowed; service handles supersede
    return email
```
**Alternatives considered**:
- Raise error for all duplicates; require explicit "resend" — forces users through an extra step for a common mistake; poor UX
- Handle in serializer — cannot be transactionally safe without moving delete-and-create into the serializer, violating HackSoftware Principle I

---

## 6. Expired Token Clean-Up

**Decision**: Delete expired `EmailVerificationToken` records at the point of rejection in `email_verification_verify` service. No periodic task required.  
**Rationale**: Eager deletion on rejection keeps the table clean without introducing Celery or a management command. Since the only code path that encounters an expired token is the verify endpoint, this is the right place. Combined with cascade deletion on user delete (resend, re-registration), the token table will remain small in practice.  
**Alternatives considered**:
- Celery periodic task — requires Celery infrastructure; disproportionate for a small table; violates Principle VI (Simplicity)
- Leave expired records — causes unbounded table growth; no operational benefit

---

## 7. Token Model Relationship

**Decision**: `OneToOneField(CustomUser, on_delete=CASCADE, related_name="email_verification_token")`.  
**Rationale**: A user can have at most one active token at any time. `OneToOneField` enforces this at the database level without an additional `unique` constraint. `CASCADE` means deleting a user (re-registration supersede path) automatically deletes the token.  
**Re-registration supersede flow**: Delete the old unverified user → old `EmailVerificationToken` is cascade-deleted → new user created → new token created.  
**Resend flow**: Delete the existing `EmailVerificationToken` for the user → create a new one.  
**Alternatives considered**:
- `ForeignKey` with `unique=True` — semantically identical to `OneToOneField`; use `OneToOneField` for explicit intent
- Separate `is_active` flag on token — adds complexity; OneToOneField + cascade achieves the same outcome with simpler logic

---

## 8. `is_email_verified` Field Placement

**Decision**: Add `is_email_verified = models.BooleanField(default=False)` directly to `CustomUser`.  
**Rationale**: The verified status is a core property of the user's authentication state — it directly gates login. Placing it on the `CustomUser` model keeps the login gate check (`user.is_email_verified`) as a simple field read with no joins. The migration will set `default=False` for all new users; a `data migration` will set existing users to `True` to grandfather them in.  
**Alternatives considered**:
- Store verified status on `EmailVerificationToken` (implied by absence of token) — breaks down when the token is deleted after verification; requires join at login gate
- Store on `Profile` — `Profile` is not loaded during authentication; adds a join at the critical login path

---

## 9. Existing Users Migration Default

**Decision**: Existing users will have `is_email_verified` set to `True` via a data migration, grandfathering all current accounts.  
**Rationale**: Retroactively requiring email verification for existing users would lock them out of their accounts. Setting `True` for existing users is the safe default.  
**Migration strategy**: One schema migration adds the field with `default=False`; a data migration (or a `RunPython` in the same migration) sets `is_email_verified=True` for all existing users (`User.objects.update(is_email_verified=True)`).

---

## Summary: All NEEDS CLARIFICATION Resolved

| Item | Resolution |
|------|-----------|
| Token generation | `secrets.token_urlsafe(32)` |
| Configurable settings | `users/conf.py` with `getattr(settings, KEY, DEFAULT)` properties |
| Email dispatch | `render_to_string` + `send_mail(html_message=...)` |
| Login gate | Override `CustomTokenObtainPairSerializer.validate()` |
| Re-registration | Service-layer supersede with `@transaction.atomic` |
| Expired token cleanup | Delete at point of rejection in verify service |
| Token relationship | `OneToOneField(CustomUser, CASCADE)` |
| `is_email_verified` placement | Field on `CustomUser` |
| Migration default | Data migration grandfathers existing users as verified |
