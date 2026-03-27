"""Profile models for extended user data."""

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models


class Profile(models.Model):
    """Extended user profile information.

    One-to-one relationship with CustomUser. Auto-created
    when a user registers via the user_create service.

    Attributes:
        user: Link to the authentication entity.
        display_name: Public display name.
        bio: Short biography/description.
        avatar: Profile picture (JPEG/PNG/WebP, max 5MB).
        phone_number: Contact number.
        date_of_birth: Birth date for age verification.
        preferences: JSON object for user settings.
        created_at: Profile creation timestamp.
        updated_at: Last modification timestamp.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="profile",
    )
    display_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Public display name",
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text="Short biography",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        help_text="Profile picture (JPEG/PNG/WebP, max 5MB)",
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Contact phone number",
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text="Birth date",
    )
    preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="User preferences and settings",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "profile"
        verbose_name_plural = "profiles"

    def __str__(self) -> str:
        """Return display name or user email."""
        return self.display_name or str(self.user)


class Policy(models.Model):
    """Conditional access rules for role-based permissions.

    Policies define additional constraints on permissions that
    are evaluated at access time (time windows, IP restrictions, etc.).

    Attributes:
        name: Unique policy identifier.
        description: Human-readable description.
        conditions: JSON object defining constraint rules.
        is_active: Whether policy is currently enforced.
        created_at: Policy creation timestamp.
        updated_at: Last modification timestamp.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique policy identifier",
    )
    description = models.TextField(
        blank=True,
        help_text="Human-readable description of the policy",
    )
    conditions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Rule conditions (time_window, ip_whitelist, etc.)",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this policy is currently enforced",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "policy"
        verbose_name_plural = "policies"
        ordering = ["name"]

    def __str__(self) -> str:
        """Return policy name."""
        return self.name


class GroupPolicy(models.Model):
    """Links Django Groups (roles) to Policies.

    Many-to-many through model allowing roles to have
    multiple policies attached with activation tracking.

    Attributes:
        group: The Django Group (role) this policy applies to.
        policy: The Policy being assigned.
        created_at: Assignment timestamp.
    """

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="group_policies",
        help_text="The role this policy applies to",
    )
    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        related_name="group_policies",
        help_text="The policy assigned to the role",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "group policy"
        verbose_name_plural = "group policies"
        unique_together = [["group", "policy"]]
        ordering = ["group__name", "policy__name"]

    def __str__(self) -> str:
        """Return group-policy relationship description."""
        return f"{self.group.name} - {self.policy.name}"
