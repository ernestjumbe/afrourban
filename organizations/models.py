"""Models for organization entities."""

from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower


class OrganizationType(models.TextChoices):
    """Supported organization classifications."""

    RESTAURANT = "restaurant", "Restaurant"
    BARBER = "barber", "Barber"
    HAIR_SALON = "hair_salon", "Hair Salon"
    BAR = "bar", "Bar"
    NIGHT_CLUB = "night_club", "Night Club"
    EVENT_ORGANIZER = "event_organizer", "Event Organizer"
    DANCE_CREW = "dance_crew", "Dance Crew"
    ONLINE_COMMUNITY = "online_community", "Online Community"
    RETAIL_STORE = "retail_store", "Retail Store"
    OTHER = "other", "Other"


class Organization(models.Model):
    """Standalone organization profile owned by a registered user."""

    NAME_MAX_LENGTH = 255
    TYPE_MAX_LENGTH = 32

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organizations",
        help_text="User who manages this organization profile.",
    )
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        help_text="Public organization name.",
    )
    description = models.TextField(
        help_text="Public organization description or bio.",
    )
    organization_type = models.CharField(
        max_length=TYPE_MAX_LENGTH,
        choices=OrganizationType.choices,
        help_text="Primary organization category.",
    )
    is_online_only = models.BooleanField(
        default=False,
        help_text="Whether the organization operates online without a storefront.",
    )
    physical_address = models.TextField(
        blank=True,
        null=True,
        help_text="Physical organization address when not online-only.",
    )
    logo = models.ImageField(
        upload_to="organizations/logos/",
        blank=True,
        null=True,
        help_text="Optional organization logo.",
    )
    cover_image = models.ImageField(
        upload_to="organizations/covers/",
        blank=True,
        null=True,
        help_text="Optional organization cover image.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "organization"
        verbose_name_plural = "organizations"
        ordering = ["-created_at", "name"]
        indexes = [
            models.Index(fields=["owner", "-created_at"]),
            models.Index(fields=["organization_type", "is_online_only"]),
            models.Index(fields=["created_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                "owner",
                Lower("name"),
                name="organizations_org_owner_name_ci_uniq",
            ),
        ]

    def __str__(self) -> str:
        """Return the public organization name."""

        return self.name

    def clean(self) -> None:
        """Enforce core organization validation constraints."""

        super().clean()

        if not self.is_online_only and not (self.physical_address or "").strip():
            raise ValidationError(
                {
                    "physical_address": [
                        "Physical address is required for organizations with a physical presence."
                    ]
                }
            )
