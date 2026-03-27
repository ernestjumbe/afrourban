"""Admin configuration for users app."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import CustomUser, WebAuthnCredential


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Admin interface for CustomUser model.

    Customizes the default UserAdmin to work with email-based
    authentication instead of username-based.
    """

    list_display = (
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
        "last_login",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "date_joined")
    search_fields = ("email",)
    ordering = ("-date_joined",)
    filter_horizontal = ("groups", "user_permissions")

    # Fieldsets for the change form
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # Fieldsets for the add form (creating new users)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )

    readonly_fields = ("date_joined", "last_login")


@admin.register(WebAuthnCredential)
class WebAuthnCredentialAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "device_label",
        "is_enabled",
        "sign_count",
        "created_at",
    )
    list_filter = ("is_enabled", "created_at")
    search_fields = ("user__email", "device_label")
    readonly_fields = (
        "credential_id",
        "public_key",
        "sign_count",
        "webauthn_user_id",
        "created_at",
    )
    raw_id_fields = ("user",)
