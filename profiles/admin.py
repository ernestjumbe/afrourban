"""Admin configuration for profiles app."""

from django.contrib import admin

from profiles.models import GroupPolicy, Policy, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin interface for Profile model."""

    list_display = (
        "user",
        "display_name",
        "phone_number",
        "date_of_birth",
        "age_verification_status",
        "age_verified_at",
        "created_at",
    )
    list_filter = ("age_verification_status", "created_at", "updated_at")
    search_fields = ("user__email", "display_name", "phone_number")
    ordering = ("-created_at",)
    readonly_fields = ("user", "age_verified_at", "created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("user", "display_name", "bio")}),
        ("Contact", {"fields": ("phone_number",)}),
        ("Personal", {"fields": ("date_of_birth", "avatar")}),
        (
            "Age Verification",
            {"fields": ("age_verification_status", "age_verified_at")},
        ),
        ("Settings", {"fields": ("preferences",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


class GroupPolicyInline(admin.TabularInline):
    """Inline admin for GroupPolicy in Policy admin."""

    model = GroupPolicy
    extra = 1
    autocomplete_fields = ["group"]


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    """Admin interface for Policy model."""

    list_display = (
        "name",
        "is_active",
        "description_preview",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [GroupPolicyInline]

    fieldsets = (
        (None, {"fields": ("name", "description", "is_active")}),
        (
            "Conditions",
            {
                "fields": ("conditions",),
                "description": (
                    "JSON conditions: time_window, ip_whitelist, require_mfa, "
                    "max_requests_per_hour"
                ),
            },
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Description")
    def description_preview(self, obj: Policy) -> str:
        """Return truncated description for list display."""
        if obj.description and len(obj.description) > 50:
            return f"{obj.description[:50]}..."
        return obj.description or "-"


@admin.register(GroupPolicy)
class GroupPolicyAdmin(admin.ModelAdmin):
    """Admin interface for GroupPolicy model."""

    list_display = ("group", "policy", "created_at")
    list_filter = ("group", "policy", "created_at")
    search_fields = ("group__name", "policy__name")
    ordering = ("-created_at",)
    autocomplete_fields = ["group", "policy"]
    readonly_fields = ("created_at",)
