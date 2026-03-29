"""Schema helpers for versioned API documentation visibility.

This module classifies API endpoints into public/authenticated/staff scopes and
provides filtered drf-spectacular schema views for public and internal docs.
"""

from __future__ import annotations

from typing import Any, Mapping

from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated

from afrourban.api_governance import (
    DEFAULT_MINIMUM_NOTICE_DAYS,
    REQUIRED_DEPRECATION_FIELDS,
    load_and_validate_deprecation_registry,
)

PUBLIC_SCOPE = "public"
AUTHENTICATED_SCOPE = "authenticated"
STAFF_SCOPE = "staff"

API_V1_PREFIX = "/api/v1/"
DOCS_PREFIX = "/api/v1/docs/"

_AUTH_PUBLIC_PREFIX = "/api/v1/auth/"
_AUTH_PUBLIC_ENDPOINT_PREFIXES = (
    "/api/v1/auth/register/",
    "/api/v1/auth/token/",
    "/api/v1/auth/email-verification/verify/",
    "/api/v1/auth/email-verification/resend/",
    "/api/v1/auth/password/reset/",
    "/api/v1/auth/passkey/register/",
    "/api/v1/auth/passkey/authenticate/",
)
_AUTHENTICATED_AUTH_PREFIXES = (
    "/api/v1/auth/logout/",
    "/api/v1/auth/password/change/",
    "/api/v1/auth/passkey/add/",
    "/api/v1/auth/passkey/",
)
_HEALTH_PREFIX = "/api/v1/health/"
_STAFF_PREFIX = "/api/v1/admin/users/"
_PROFILES_PREFIX = "/api/v1/profiles/"


def classify_endpoint_scope(path: str) -> str | None:
    """Return endpoint scope for a versioned API path.

    Returns ``None`` for non-versioned or documentation routes.
    """

    if not path.startswith(API_V1_PREFIX):
        return None

    if path.startswith(DOCS_PREFIX):
        return None

    if path.startswith(_HEALTH_PREFIX):
        return PUBLIC_SCOPE

    if path.startswith(_STAFF_PREFIX):
        return STAFF_SCOPE

    if path.startswith(_PROFILES_PREFIX):
        return AUTHENTICATED_SCOPE

    if path.startswith(_AUTH_PUBLIC_PREFIX):
        if path.startswith(_AUTH_PUBLIC_ENDPOINT_PREFIXES):
            return PUBLIC_SCOPE
        if path.startswith(_AUTHENTICATED_AUTH_PREFIXES):
            return AUTHENTICATED_SCOPE
        return AUTHENTICATED_SCOPE

    return AUTHENTICATED_SCOPE


class _ScopedSchemaGenerator(SchemaGenerator):
    """Filter schema paths by endpoint visibility scope."""

    allowed_scopes: tuple[str, ...] = ()

    def parse(self, input_request: Any, public: bool) -> dict[str, dict[str, Any]]:
        all_paths = super().parse(input_request=input_request, public=public)
        filtered_paths: dict[str, dict[str, Any]] = {}

        for path, operations in all_paths.items():
            scope = classify_endpoint_scope(path)
            if scope is None or scope not in self.allowed_scopes:
                continue

            filtered_paths[path] = {}
            for method, operation in operations.items():
                # Surface the visibility contract in generated operations.
                operation.setdefault("x-access-scope", scope)
                filtered_paths[path][method] = operation

        return filtered_paths


class PublicSchemaGenerator(_ScopedSchemaGenerator):
    """Generator for public schema view."""

    allowed_scopes = (PUBLIC_SCOPE,)


class InternalSchemaGenerator(_ScopedSchemaGenerator):
    """Generator for authenticated internal schema view."""

    allowed_scopes = (PUBLIC_SCOPE, AUTHENTICATED_SCOPE, STAFF_SCOPE)

    def get_schema(self, request: Any = None, public: bool = False) -> dict[str, Any]:
        schema = super().get_schema(request=request, public=public)
        if schema is None:
            return {}

        schema["x-deprecations"] = _deprecation_schema_metadata()
        return schema


def _deprecation_schema_metadata() -> dict[str, Any]:
    """Build validated deprecation metadata extension for internal schema."""

    registry = load_and_validate_deprecation_registry()
    policy = registry.get("policy", {})

    minimum_notice_days = DEFAULT_MINIMUM_NOTICE_DAYS
    required_fields = list(REQUIRED_DEPRECATION_FIELDS)

    if isinstance(policy, Mapping):
        configured_days = policy.get("minimum_notice_days")
        if isinstance(configured_days, int):
            minimum_notice_days = configured_days

        configured_fields = policy.get("required_fields")
        if isinstance(configured_fields, list):
            required_fields = [str(field) for field in configured_fields]

    return {
        "minimum_notice_days": minimum_notice_days,
        "required_fields": required_fields,
        "versions": registry.get("versions", []),
        "endpoints": registry.get("endpoints", []),
    }


class PublicSchemaAPIView(SpectacularAPIView):
    """Serve public OpenAPI schema (public endpoints only)."""

    generator_class = PublicSchemaGenerator
    permission_classes = [AllowAny]
    authentication_classes = []
    serve_public = True
    custom_settings = {
        "TITLE": "Afrourban Public API",
        "VERSION": "v1",
    }


class InternalSchemaAPIView(SpectacularAPIView):
    """Serve internal OpenAPI schema (all active endpoints)."""

    generator_class = InternalSchemaGenerator
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    serve_public = True
    custom_settings = {
        "TITLE": "Afrourban Internal API",
        "VERSION": "v1",
    }


class PublicSchemaSwaggerView(SpectacularSwaggerView):
    """Serve public Swagger UI for anonymous and authenticated users."""

    permission_classes = [AllowAny]
    authentication_classes = []


class InternalSchemaSwaggerView(SpectacularSwaggerView):
    """Serve internal Swagger UI for authenticated users only."""

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
