"""Custom user model with email-based authentication."""

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from users.managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Custom user model using email as the primary identifier.

    Uses AbstractBaseUser for core authentication functionality and
    PermissionsMixin for Django's permission system integration.

    Attributes:
        email: Primary login identifier (unique, case-insensitive).
        is_active: Whether the user account is enabled.
        is_staff: Whether the user can access Django admin.
        date_joined: Timestamp when the account was created.
    """

    email = models.EmailField(
        "email address",
        max_length=255,
        unique=True,
        db_index=True,
    )
    is_active = models.BooleanField(
        "active",
        default=True,
        help_text=(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    is_staff = models.BooleanField(
        "staff status",
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    is_email_verified = models.BooleanField(
        "email verified",
        default=False,
        help_text="Designates whether the user has verified their email address.",
    )
    date_joined = models.DateTimeField("date joined", default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["is_active", "is_staff"]),
        ]

    def __str__(self) -> str:
        """Return the email as the string representation."""
        return self.email

    def clean(self) -> None:
        """Normalize the email address."""
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)


class EmailVerificationToken(models.Model):
    """One-time token for verifying a user's email address.

    Each user has at most one active token at a time (enforced by OneToOneField).
    Tokens are deleted upon successful verification or expiry rejection.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_verification_token",
    )
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = "email verification token"
        verbose_name_plural = "email verification tokens"

    def __str__(self) -> str:
        return f"EmailVerificationToken(user={self.user_id})"


class WebAuthnCredential(models.Model):
    """A WebAuthn passkey credential registered by a user.

    Stores the public key material and metadata needed to verify
    authentication assertions. Each user may have up to 5 credentials
    (enforced at the service layer).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="webauthn_credentials",
    )
    credential_id = models.BinaryField(
        max_length=1024,
        unique=True,
        help_text="WebAuthn credential identifier (opaque bytes from authenticator).",
    )
    public_key = models.BinaryField(
        max_length=1024,
        help_text="COSE-encoded public key for signature verification.",
    )
    sign_count = models.PositiveIntegerField(
        default=0,
        help_text="Signature counter for cloning detection.",
    )
    webauthn_user_id = models.BinaryField(
        max_length=64,
        help_text="Random user handle used during registration (NOT the DB PK).",
    )
    device_label = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="User-provided or auto-generated device label.",
    )
    is_enabled = models.BooleanField(
        default=True,
        help_text="False when disabled (e.g., cloning detected).",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "WebAuthn credential"
        verbose_name_plural = "WebAuthn credentials"
        indexes = [
            models.Index(fields=["user", "is_enabled"]),
        ]

    def __str__(self) -> str:
        label = self.device_label or "unnamed"
        return f"WebAuthnCredential({label}, user={self.user_id})"
