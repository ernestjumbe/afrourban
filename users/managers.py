"""Custom user manager for email-based authentication."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib.auth.models import BaseUserManager

if TYPE_CHECKING:
    from users.models import CustomUser


class CustomUserManager(BaseUserManager["CustomUser"]):
    """Manager for CustomUser model with email-based authentication.

    Provides methods for creating regular users and superusers
    using email as the primary identifier instead of username.
    """

    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> "CustomUser":
        """Create and save a regular user with the given email and password.

        Args:
            email: The user's email address (used as username).
            password: The user's password (will be hashed).
            **extra_fields: Additional fields to set on the user model.

        Returns:
            The created CustomUser instance.

        Raises:
            ValueError: If email is not provided.
        """
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        username = extra_fields.get("username")
        if username is None or (
            isinstance(username, str) and username.strip() == ""
        ):
            extra_fields["username"] = email

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> "CustomUser":
        """Create and save a superuser with the given email and password.

        Args:
            email: The superuser's email address.
            password: The superuser's password (will be hashed).
            **extra_fields: Additional fields to set on the user model.

        Returns:
            The created CustomUser superuser instance.

        Raises:
            ValueError: If is_staff or is_superuser is not True.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
