"""Add email verification support.

1. Add ``is_email_verified`` field to ``CustomUser``.
2. Grandfather all existing users as verified (data migration).
3. Create ``EmailVerificationToken`` model.
"""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def set_existing_users_verified(apps, schema_editor):
    """Mark all pre-existing users as email-verified."""
    CustomUser = apps.get_model("users", "CustomUser")
    CustomUser.objects.update(is_email_verified=True)


def noop(apps, schema_editor):
    """Reverse is a no-op; the field default (False) is acceptable."""


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        # Step 1: Add is_email_verified to CustomUser
        migrations.AddField(
            model_name="customuser",
            name="is_email_verified",
            field=models.BooleanField(
                default=False,
                help_text="Designates whether the user has verified their email address.",
                verbose_name="email verified",
            ),
        ),
        # Step 2: Grandfather existing users
        migrations.RunPython(set_existing_users_verified, noop),
        # Step 3: Create EmailVerificationToken table
        migrations.CreateModel(
            name="EmailVerificationToken",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "token",
                    models.CharField(db_index=True, max_length=64, unique=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField()),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="email_verification_token",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "email verification token",
                "verbose_name_plural": "email verification tokens",
            },
        ),
    ]
