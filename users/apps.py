"""Users app configuration."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Configuration for the users Django app.

    Handles custom user authentication and authorization.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
    verbose_name = "Users"
