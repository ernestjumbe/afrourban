"""Profile services for write operations.

Following HackSoftware Django Styleguide - services
are used for all write operations (mutations).
"""

from __future__ import annotations

import os
import uuid
from typing import Any

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from profiles.models import Profile


@transaction.atomic
def profile_update(
    *,
    profile: Profile,
    display_name: str | None = None,
    bio: str | None = None,
    phone_number: str | None = None,
    date_of_birth: Any | None = None,
    preferences: dict[str, Any] | None = None,
) -> Profile:
    """Update profile fields.

    Only updates fields that are explicitly provided (not None).
    Preferences are partially merged with existing values.

    Args:
        profile: The profile to update.
        display_name: New display name (optional).
        bio: New biography (optional).
        phone_number: New phone number (optional).
        date_of_birth: New birth date (optional).
        preferences: Preferences dict to merge (optional).

    Returns:
        Updated profile instance.
    """
    fields_to_update: list[str] = []

    if display_name is not None:
        profile.display_name = display_name
        fields_to_update.append("display_name")

    if bio is not None:
        profile.bio = bio
        fields_to_update.append("bio")

    if phone_number is not None:
        profile.phone_number = phone_number
        fields_to_update.append("phone_number")

    if date_of_birth is not None:
        profile.date_of_birth = date_of_birth
        fields_to_update.append("date_of_birth")

    if preferences is not None:
        # Merge with existing preferences (shallow merge)
        current_preferences = profile.preferences or {}
        current_preferences.update(preferences)
        profile.preferences = current_preferences
        fields_to_update.append("preferences")

    if fields_to_update:
        # Always update updated_at
        fields_to_update.append("updated_at")
        profile.save(update_fields=fields_to_update)

    return profile


def _generate_avatar_filename(original_name: str, user_id: int) -> str:
    """Generate unique filename for avatar.

    Args:
        original_name: Original uploaded filename.
        user_id: User ID for filename prefix.

    Returns:
        Unique filename with user ID and UUID.
    """
    ext = os.path.splitext(original_name)[1].lower()
    unique_id = uuid.uuid4().hex[:8]
    return f"{user_id}_{unique_id}{ext}"


@transaction.atomic
def avatar_upload(*, profile: Profile, avatar_file: UploadedFile) -> str:
    """Upload new avatar image.

    Deletes existing avatar if present before saving new one.

    Args:
        profile: The profile to update.
        avatar_file: The uploaded image file.

    Returns:
        URL of the uploaded avatar.
    """
    # Delete existing avatar if present
    if profile.avatar:
        profile.avatar.delete(save=False)

    # Generate unique filename
    filename = _generate_avatar_filename(avatar_file.name, profile.user_id)
    profile.avatar.save(filename, avatar_file, save=True)

    return profile.avatar.url


@transaction.atomic
def avatar_delete(*, profile: Profile) -> None:
    """Delete avatar image from profile.

    Args:
        profile: The profile to update.
    """
    if profile.avatar:
        profile.avatar.delete(save=False)
        profile.avatar = None
        profile.save(update_fields=["avatar", "updated_at"])


# =============================================================================
# Policy Services (Phase 7: User Story 5)
# =============================================================================


def policy_evaluate(
    *,
    policy: "Policy",
    context: dict[str, Any] | None = None,
) -> tuple[bool, str | None]:
    """Evaluate a policy's conditions against the provided context.

    Checks each condition type in the policy against the context.
    Returns early on first failure.

    Args:
        policy: The Policy instance to evaluate.
        context: Context dict with request info (ip_address, timestamp, etc.).

    Returns:
        Tuple of (passes: bool, reason: str | None).
        reason is None if passes is True, otherwise explains the failure.
    """
    from datetime import datetime

    import pytz

    from profiles.models import Policy

    if not policy.is_active:
        return True, None  # Inactive policies always pass

    conditions = policy.conditions or {}
    ctx = context or {}

    # Check time_window condition
    if "time_window" in conditions:
        tw = conditions["time_window"]
        tz_name = tw.get("timezone", "UTC")
        try:
            tz = pytz.timezone(tz_name)
        except pytz.UnknownTimeZoneError:
            tz = pytz.UTC

        now = ctx.get("timestamp", datetime.now(tz))
        if now.tzinfo is None:
            now = tz.localize(now)
        else:
            now = now.astimezone(tz)

        current_time = now.strftime("%H:%M")
        start_time = tw.get("start", "00:00")
        end_time = tw.get("end", "23:59")

        if not (start_time <= current_time <= end_time):
            return False, f"Access restricted to {start_time}-{end_time} {tz_name}"

    # Check ip_whitelist condition
    if "ip_whitelist" in conditions:
        from ipaddress import ip_address, ip_network

        whitelist = conditions["ip_whitelist"]
        client_ip = ctx.get("ip_address")

        if client_ip and whitelist:
            try:
                client = ip_address(client_ip)
                allowed = any(
                    client in ip_network(net, strict=False) for net in whitelist
                )
                if not allowed:
                    return False, "IP address not in allowed range"
            except ValueError:
                return False, "Invalid IP address format"

    # Check require_mfa condition
    if conditions.get("require_mfa"):
        has_mfa = ctx.get("mfa_verified", False)
        if not has_mfa:
            return False, "Multi-factor authentication required"

    return True, None


def policies_evaluate_for_user(
    *,
    user: Any,
    context: dict[str, Any] | None = None,
) -> tuple[bool, list[str]]:
    """Evaluate all active policies for a user's roles.

    Args:
        user: The user instance.
        context: Context dict with request info.

    Returns:
        Tuple of (all_pass: bool, failure_reasons: list[str]).
    """
    from profiles.models import GroupPolicy

    # Get all policies from user's groups
    group_ids = user.groups.values_list("id", flat=True)
    group_policies = GroupPolicy.objects.filter(
        group_id__in=group_ids,
        policy__is_active=True,
    ).select_related("policy")

    failures = []
    for gp in group_policies:
        passes, reason = policy_evaluate(policy=gp.policy, context=context)
        if not passes and reason:
            failures.append(f"{gp.policy.name}: {reason}")

    return len(failures) == 0, failures
