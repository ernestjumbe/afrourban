"""URL configuration for afrourban project.

API routes are centrally registered in ``api_urlpatterns`` and included under
the ``/api/`` path prefix.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from afrourban.api_schema import (
    InternalSchemaAPIView,
    InternalSchemaSwaggerView,
    PublicSchemaAPIView,
    PublicSchemaSwaggerView,
)
from profiles.urls import api_v1_urlpatterns as profiles_api_v1_urlpatterns
from users.urls import api_v1_urlpatterns as users_api_v1_urlpatterns

api_v1_urlpatterns = [
    path("", include((users_api_v1_urlpatterns, "users-v1"))),
    path("profiles/", include((profiles_api_v1_urlpatterns, "profiles-v1"))),
    path(
        "docs/public/schema/",
        PublicSchemaAPIView.as_view(),
        name="api-schema-public",
    ),
    path(
        "docs/public/",
        PublicSchemaSwaggerView.as_view(url_name="api-schema-public"),
        name="api-docs-public",
    ),
    path(
        "docs/internal/schema/",
        InternalSchemaAPIView.as_view(),
        name="api-schema-internal",
    ),
    path(
        "docs/internal/",
        InternalSchemaSwaggerView.as_view(url_name="api-schema-internal"),
        name="api-docs-internal",
    ),
]

api_urlpatterns = [
    path("v1/", include(api_v1_urlpatterns)),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urlpatterns)),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    # Serve static and media files from development server
    # urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
