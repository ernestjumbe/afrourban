"""Health app configuration."""

from django.apps import AppConfig


class HealthConfig(AppConfig):
    """Configuration for the health Django app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "health"
    verbose_name = "Health"
