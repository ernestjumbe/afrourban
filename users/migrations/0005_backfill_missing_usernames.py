from __future__ import annotations

from django.db import migrations


USERNAME_STORAGE_MAX_LENGTH = 255


def _is_blank_username(username: str | None) -> bool:
    return username is None or username.strip() == ""


def _build_collision_safe_username(
    *,
    email: str,
    user_id: int,
    reserved_usernames: set[str],
) -> str:
    candidate = email
    lowered_candidate = candidate.lower()
    if lowered_candidate not in reserved_usernames:
        return candidate

    base_suffix = f"__legacy_{user_id}"
    max_base_length = USERNAME_STORAGE_MAX_LENGTH - len(base_suffix)
    candidate = f"{email[:max_base_length]}{base_suffix}"
    lowered_candidate = candidate.lower()

    counter = 1
    while lowered_candidate in reserved_usernames:
        suffix = f"{base_suffix}_{counter}"
        max_base_length = USERNAME_STORAGE_MAX_LENGTH - len(suffix)
        candidate = f"{email[:max_base_length]}{suffix}"
        lowered_candidate = candidate.lower()
        counter += 1

    return candidate


def backfill_missing_usernames(apps, schema_editor):
    CustomUser = apps.get_model("users", "CustomUser")

    reserved_usernames: set[str] = set()
    for user in CustomUser.objects.only("username").order_by("pk"):
        if not _is_blank_username(user.username):
            reserved_usernames.add(user.username.lower())

    users_to_update = []
    for user in CustomUser.objects.only("id", "email", "username").order_by("pk"):
        if not _is_blank_username(user.username):
            continue

        username = _build_collision_safe_username(
            email=user.email,
            user_id=user.pk,
            reserved_usernames=reserved_usernames,
        )
        user.username = username
        users_to_update.append(user)
        reserved_usernames.add(username.lower())

    if users_to_update:
        CustomUser.objects.bulk_update(users_to_update, ["username"])


def noop(apps, schema_editor):
    """Backfill does not reverse cleanly; keep reverse as a no-op."""


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_add_username_fields"),
    ]

    operations = [
        migrations.RunPython(backfill_missing_usernames, noop),
    ]
