"""URL configuration for the health app.

Exported route groups:
- `api_v1_urlpatterns` for canonical inclusion under `/api/v1/`
"""

from django.urls import path

from health.views import HealthView

app_name = "health"

api_v1_urlpatterns: list = [
    path("health/", HealthView.as_view(), name="health"),
]

urlpatterns = api_v1_urlpatterns
