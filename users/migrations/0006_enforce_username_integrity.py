import django.db.models.functions.text
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_backfill_missing_usernames"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="customuser",
            name="users_custom_username_ci_idx",
        ),
        migrations.AlterField(
            model_name="customuser",
            name="username",
            field=models.CharField(
                db_index=True,
                help_text=(
                    "Account username. User-supplied values must match project "
                    "username rules; legacy rows may be backfilled from email."
                ),
                max_length=255,
                verbose_name="username",
            ),
        ),
        migrations.AddConstraint(
            model_name="customuser",
            constraint=models.CheckConstraint(
                condition=~models.Q(username=""),
                name="users_custom_username_non_empty",
            ),
        ),
        migrations.AddConstraint(
            model_name="customuser",
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower("username"),
                name="users_custom_username_ci_uniq",
            ),
        ),
    ]
