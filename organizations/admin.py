"""Admin registration for organizations models."""

from django.contrib import admin

from organizations.models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin interface for organization records."""

    list_display = (
        "name",
        "owner",
        "organization_type",
        "is_online_only",
        "created_at",
        "updated_at",
    )
    list_filter = ("organization_type", "is_online_only", "created_at", "updated_at")
    search_fields = ("name", "description", "owner__email")
    ordering = ("-created_at", "name")
    raw_id_fields = ("owner",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "owner",
                    "name",
                    "description",
                    "organization_type",
                )
            },
        ),
        (
            "Presence",
            {
                "fields": (
                    "is_online_only",
                    "physical_address",
                )
            },
        ),
        (
            "Branding",
            {
                "fields": (
                    "logo",
                    "cover_image",
                )
            },
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
