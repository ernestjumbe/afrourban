"""URL configuration for profiles app.

Mounted at /api/profiles/ in main urls.py.

Routes:
- /me/ - GET, PATCH current user's profile
- /me/avatar/ - POST, DELETE avatar
- /{user_id}/ - GET public profile
"""

from django.urls import path

from profiles.views import ProfileAvatarView, ProfileMeView, ProfilePublicView

app_name = "profiles"

urlpatterns = [
    path("me/", ProfileMeView.as_view(), name="me"),
    path("me/avatar/", ProfileAvatarView.as_view(), name="me-avatar"),
    path("<int:user_id>/", ProfilePublicView.as_view(), name="public"),
]
