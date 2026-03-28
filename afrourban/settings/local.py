# ruff: noqa: F403,F405

from .base import *
from .secrets import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

INSTALLED_APPS += [
    "debug_toolbar",
    "django_extensions",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ALLOWED_HOSTS = ["*"]


# Database configuration - supports both SQLite and PostgreSQL
if SQL_ENGINE == "django.db.backends.sqlite3":
    DATABASES = {
        "default": {
            "ENGINE": SQL_ENGINE,
            "NAME": BASE_DIR / SQL_DATABASE,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": SQL_ENGINE,
            "NAME": SQL_DATABASE,
            "USER": SQL_USER,
            "PASSWORD": SQL_PASSWORD,
            "HOST": SQL_HOST,
            "PORT": int(SQL_PORT) if SQL_PORT else 5432,
        }
    }

STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_URL = "static/"

MEDIA_URL = "/media/"

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# WebAuthn / Passkey settings
USERS_WEBAUTHN_RP_ID = "localhost"
USERS_WEBAUTHN_RP_NAME = "Afrourban"
USERS_WEBAUTHN_ORIGIN = "http://localhost:8000"
USERS_WEBAUTHN_CHALLENGE_TIMEOUT_SECONDS = 300  # 5 minutes
USERS_WEBAUTHN_MAX_CREDENTIALS_PER_USER = 5

HTML_MINIFY = False

EMAIL_HOST = "email"
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_PORT = 1025
EMAIL_USE_TLS = False


def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
    "INSERT_BEFORE": "</head>",
    "RENDER_PANELS": True,
}
