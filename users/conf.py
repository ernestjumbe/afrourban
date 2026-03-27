"""App-level settings for the users application.

Follows the standard Django third-party app pattern (used by DRF, Simple JWT, etc.)
where defaults are centralised in a module and overridable via the project settings.

Usage::

    from users.conf import app_settings

    expiry = app_settings.EMAIL_VERIFICATION_TOKEN_EXPIRY_DAYS
"""

from __future__ import annotations

from django.conf import settings


class _AppSettings:
    """Lazy settings accessor for the users app.

    Each property reads from ``django.conf.settings`` at access time,
    falling back to a sensible default when the key is absent.
    """

    @property
    def EMAIL_VERIFICATION_TOKEN_EXPIRY_DAYS(self) -> int:
        return getattr(settings, "USERS_EMAIL_VERIFICATION_TOKEN_EXPIRY_DAYS", 7)

    @property
    def EMAIL_VERIFICATION_BASE_URL(self) -> str:
        return getattr(settings, "USERS_EMAIL_VERIFICATION_BASE_URL", "")

    @property
    def EMAIL_VERIFICATION_FROM_EMAIL(self) -> str:
        return getattr(
            settings, "USERS_EMAIL_VERIFICATION_FROM_EMAIL", settings.DEFAULT_FROM_EMAIL
        )

    @property
    def EMAIL_VERIFICATION_SITE_NAME(self) -> str:
        return getattr(settings, "USERS_EMAIL_VERIFICATION_SITE_NAME", "Afrourban")

    @property
    def WEBAUTHN_RP_ID(self) -> str:
        return getattr(settings, "USERS_WEBAUTHN_RP_ID", "localhost")

    @property
    def WEBAUTHN_RP_NAME(self) -> str:
        return getattr(settings, "USERS_WEBAUTHN_RP_NAME", "Afrourban")

    @property
    def WEBAUTHN_ORIGIN(self) -> str:
        return getattr(settings, "USERS_WEBAUTHN_ORIGIN", "http://localhost:8000")

    @property
    def WEBAUTHN_CHALLENGE_TIMEOUT_SECONDS(self) -> int:
        return getattr(settings, "USERS_WEBAUTHN_CHALLENGE_TIMEOUT_SECONDS", 300)

    @property
    def WEBAUTHN_MAX_CREDENTIALS_PER_USER(self) -> int:
        return getattr(settings, "USERS_WEBAUTHN_MAX_CREDENTIALS_PER_USER", 5)


app_settings = _AppSettings()
