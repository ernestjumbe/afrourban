"""URL configuration for users app.

Exported route groups:
- `api_v1_urlpatterns` for canonical inclusion under `/api/v1/`
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
    PasskeyAddCompleteView,
    PasskeyAddOptionsView,
    PasskeyAuthenticateCompleteView,
    PasskeyAuthenticateOptionsView,
    PasskeyListView,
    PasskeyRegisterCompleteView,
    PasskeyRegisterOptionsView,
    PasskeyRemoveView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
    ResendVerificationEmailView,
    TokenRefreshView,
    TokenVerifyView,
    UsernameChangeView,
    VerifyEmailView,
)

app_name = "users"

# Public authentication URLs (mounted at /api/v1/auth/)
public_auth_urlpatterns: list = [
    path("register/", RegisterView.as_view(), name="register"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
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
    # Passkey registration
    path(
        "passkey/register/options/",
        PasskeyRegisterOptionsView.as_view(),
        name="passkey_register_options",
    ),
    path(
        "passkey/register/complete/",
        PasskeyRegisterCompleteView.as_view(),
        name="passkey_register_complete",
    ),
    # Passkey authentication
    path(
        "passkey/authenticate/options/",
        PasskeyAuthenticateOptionsView.as_view(),
        name="passkey_authenticate_options",
    ),
    path(
        "passkey/authenticate/complete/",
        PasskeyAuthenticateCompleteView.as_view(),
        name="passkey_authenticate_complete",
    ),
]

# Authenticated authentication URLs (mounted at /api/v1/auth/)
authenticated_auth_urlpatterns: list = [
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password/change/", PasswordChangeView.as_view(), name="password_change"),
    path("username/", UsernameChangeView.as_view(), name="username_change"),
    # Passkey add to existing account
    path(
        "passkey/add/options/",
        PasskeyAddOptionsView.as_view(),
        name="passkey_add_options",
    ),
    path(
        "passkey/add/complete/",
        PasskeyAddCompleteView.as_view(),
        name="passkey_add_complete",
    ),
    # Passkey management
    path(
        "passkey/",
        PasskeyListView.as_view(),
        name="passkey_list",
    ),
    path(
        "passkey/<int:credential_id>/",
        PasskeyRemoveView.as_view(),
        name="passkey_remove",
    ),
]

auth_urlpatterns: list = [
    *public_auth_urlpatterns,
    *authenticated_auth_urlpatterns,
]

# Admin user management URLs (mounted at /api/v1/admin/users/)
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

api_v1_auth_urlpatterns: list = [
    path("auth/", include((auth_urlpatterns, "auth"))),
]

api_v1_admin_urlpatterns: list = [
    path("admin/users/", include((admin_urlpatterns, "admin-users"))),
]

api_v1_urlpatterns: list = [
    *api_v1_auth_urlpatterns,
    *api_v1_admin_urlpatterns,
]

# Canonical versioned routes for module-level includes.
urlpatterns = api_v1_urlpatterns
