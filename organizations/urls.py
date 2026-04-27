"""URL configuration for the organizations app.

Exported route groups:
- `api_v1_urlpatterns` for canonical inclusion under `/api/v1/organizations/`
"""

from django.urls import path

from organizations.views import (
    OrganizationCollectionView,
    OrganizationCoverView,
    OrganizationDetailView,
    OrganizationLogoView,
)

app_name = "organizations"

api_v1_urlpatterns: list = [
    path("", OrganizationCollectionView.as_view(), name="collection"),
    path("<int:organization_id>/", OrganizationDetailView.as_view(), name="detail"),
    path("<int:organization_id>/logo/", OrganizationLogoView.as_view(), name="logo"),
    path(
        "<int:organization_id>/cover/",
        OrganizationCoverView.as_view(),
        name="cover",
    ),
]

# Canonical versioned routes for module-level includes.
urlpatterns = api_v1_urlpatterns
