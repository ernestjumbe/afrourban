"""URL configuration for the events app.

Exported route groups:
- `api_v1_urlpatterns` for canonical inclusion under `/api/v1/events/`
"""

from django.urls import path

from events.views import EventCollectionView, EventCoverView, EventDetailView

app_name = "events"

api_v1_urlpatterns: list = [
    path("", EventCollectionView.as_view(), name="collection"),
    path("<int:event_id>/", EventDetailView.as_view(), name="detail"),
    path("<int:event_id>/cover/", EventCoverView.as_view(), name="cover"),
]

# Canonical versioned routes for module-level includes.
urlpatterns = api_v1_urlpatterns
