"""URL configuration for users app.

This module defines URL patterns for:
- Authentication endpoints: /api/auth/*
- Password management: /api/auth/password/*
- Admin user management: /api/admin/users/*
- Admin role management: /api/admin/users/roles/*
"""

from django.urls import include, path

from users.views import (
    AdminRoleDetailView,
    AdminRoleListView,
    AdminUserActivateView,
    AdminUserDeactivateView,
    AdminUserDetailView,
    AdminUserListView,
    AdminUserPermissionsView,
    CustomTokenObtainPairView,
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
    ResendVerificationEmailView,
    TokenRefreshView,
    TokenVerifyView,
    VerifyEmailView,
)

app_name = "users"

# Authentication URLs (mounted at /api/auth/)
auth_urlpatterns: list = [
    path("register/", RegisterView.as_view(), name="register"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # Email verification
    path(
        "email-verification/verify/",
        VerifyEmailView.as_view(),
        name="email_verification_verify",
    ),
    path(
        "email-verification/resend/",
        ResendVerificationEmailView.as_view(),
        name="email_verification_resend",
    ),
    # Password management
    path(
        "password/reset/",
        PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("password/change/", PasswordChangeView.as_view(), name="password_change"),
]

# Admin user management URLs (mounted at /api/admin/users/)
admin_urlpatterns: list = [
    path("", AdminUserListView.as_view(), name="admin-user-list"),
    path("roles/", AdminRoleListView.as_view(), name="admin-role-list"),
    path(
        "roles/<int:role_id>/", AdminRoleDetailView.as_view(), name="admin-role-detail"
    ),
    path("<int:user_id>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
    path(
        "<int:user_id>/activate/",
        AdminUserActivateView.as_view(),
        name="admin-user-activate",
    ),
    path(
        "<int:user_id>/deactivate/",
        AdminUserDeactivateView.as_view(),
        name="admin-user-deactivate",
    ),
    path(
        "<int:user_id>/permissions/",
        AdminUserPermissionsView.as_view(),
        name="admin-user-permissions",
    ),
]

urlpatterns = [
    path("auth/", include((auth_urlpatterns, "auth"))),
    path("admin/users/", include((admin_urlpatterns, "admin-users"))),
]
