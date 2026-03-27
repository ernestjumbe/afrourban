"""Profiles app configuration."""

from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    """Configuration for the profiles Django app.

    Handles extended user profile data, roles, and policies.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "profiles"
    verbose_name = "Profiles"
