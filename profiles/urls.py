"""URL configuration for profiles app.

Mounted at /api/profiles/ in main urls.py.

Routes:
- /me/ - GET, PATCH current user's profile
- /me/avatar/ - POST, DELETE avatar
- /policies/{policy_id}/check/ - GET policy check
- /{user_id}/ - GET public profile
"""

from django.urls import path

from profiles.views import (
    PolicyCheckView,
    ProfileAvatarView,
    ProfileMeView,
    ProfilePublicView,
)

app_name = "profiles"

urlpatterns = [
    path("me/", ProfileMeView.as_view(), name="me"),
    path("me/avatar/", ProfileAvatarView.as_view(), name="me-avatar"),
    path(
        "policies/<int:policy_id>/check/",
        PolicyCheckView.as_view(),
        name="policy-check",
    ),
    path("<int:user_id>/", ProfilePublicView.as_view(), name="public"),
]
