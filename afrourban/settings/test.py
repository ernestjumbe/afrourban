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

# WebAuthn / Passkey settings for test environment
USERS_WEBAUTHN_RP_ID = "localhost"
USERS_WEBAUTHN_RP_NAME = "Afrourban"
USERS_WEBAUTHN_ORIGIN = "http://localhost:8000"
USERS_WEBAUTHN_CHALLENGE_TIMEOUT_SECONDS = 300
USERS_WEBAUTHN_MAX_CREDENTIALS_PER_USER = 5

# Username-change cooldown override for tests (feature 006 placeholder).
USERS_USERNAME_CHANGE_COOLDOWN_DAYS = 7
