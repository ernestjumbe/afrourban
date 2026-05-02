"""Admin registration for events models."""

from django.contrib import admin

from events.models import Event, EventAuditEntry


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin interface for event records."""

    list_display = (
        "title",
        "organizer_type",
        "owner",
        "organization",
        "category",
        "start_at",
        "end_at",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "category",
        "location_type",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "title",
        "description",
        "owner__email",
        "organization__name",
    )
    ordering = ("-created_at", "title")
    raw_id_fields = ("owner", "organization")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "owner",
                    "organization",
                    "title",
                    "description",
                    "category",
                )
            },
        ),
        (
            "Schedule",
            {
                "fields": (
                    "start_at",
                    "end_at",
                )
            },
        ),
        (
            "Location",
            {
                "fields": (
                    "location_type",
                    "location_web_url",
                    "location_country",
                    "location_state",
                    "location_city",
                    "location_postcode",
                )
            },
        ),
        (
            "Media",
            {
                "fields": (
                    "cover_image",
                    "tickets_url",
                )
            },
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(EventAuditEntry)
class EventAuditEntryAdmin(admin.ModelAdmin):
    """Admin interface for immutable event audit entries."""

    list_display = (
        "event",
        "field_name",
        "actor",
        "changed_at",
    )
    list_filter = ("field_name", "changed_at")
    search_fields = (
        "event__title",
        "actor__email",
        "old_value",
        "new_value",
    )
    ordering = ("-changed_at", "-id")
    raw_id_fields = ("event", "actor")
    readonly_fields = (
        "event",
        "field_name",
        "old_value",
        "new_value",
        "actor",
        "changed_at",
    )
