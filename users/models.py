"""Custom user model with email-based authentication."""

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
