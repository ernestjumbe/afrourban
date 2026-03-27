"""Test settings for afrourban project.

Inherits from base settings with overrides suitable for the test runner:
- SQLite in-memory database
- In-memory email backend
- No debug toolbar
"""

from .base import *  # noqa: F401,F403
from .secrets import *  # noqa: F401,F403

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
