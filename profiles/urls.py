"""URL configuration for profiles app.

Exported route groups:
- `api_v1_urlpatterns` for canonical inclusion under `/api/v1/profiles/`
"""

from django.urls import path

from profiles.views import (
    PolicyCheckView,
    ProfileAvatarView,
    ProfileMeView,
    ProfilePublicView,
)

app_name = "profiles"

# Authenticated profile URLs (mounted at /api/v1/profiles/)
authenticated_profile_urlpatterns: list = [
    path("me/", ProfileMeView.as_view(), name="me"),
    path("me/avatar/", ProfileAvatarView.as_view(), name="me-avatar"),
    path(
        "policies/<int:policy_id>/check/",
        PolicyCheckView.as_view(),
        name="policy-check",
    ),
    path("<int:user_id>/", ProfilePublicView.as_view(), name="public"),
]

api_v1_urlpatterns: list = authenticated_profile_urlpatterns

# Canonical versioned routes for module-level includes.
urlpatterns = api_v1_urlpatterns
