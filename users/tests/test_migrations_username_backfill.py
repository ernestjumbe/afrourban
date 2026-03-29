"""Migration tests for username backfill behavior (feature 006)."""

from __future__ import annotations

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

pytestmark = pytest.mark.django_db(transaction=True)

MIGRATE_FROM = [("users", "0004_add_username_fields")]
MIGRATE_TO = [("users", "0006_enforce_username_integrity")]


@pytest.fixture
def migrate_state(transactional_db):
    """Migrate the database schema to an arbitrary target and restore it after."""

    current_targets = MigrationExecutor(connection).loader.graph.leaf_nodes()

    def runner(targets: list[tuple[str, str]]):
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(targets)
        return executor.loader.project_state(targets).apps

    yield runner

    executor = MigrationExecutor(connection)
    executor.loader.build_graph()
    executor.migrate(current_targets)


def test_backfill_populates_missing_and_blank_usernames_from_email(migrate_state):
    """Null, empty, and whitespace-only usernames should be populated."""

    old_apps = migrate_state(MIGRATE_FROM)
    User = old_apps.get_model("users", "CustomUser")

    null_user = User.objects.create(
        email="null@example.com",
        password="not-used",
        username=None,
        is_email_verified=True,
    )
    empty_user = User.objects.create(
        email="empty@example.com",
        password="not-used",
        username="",
        is_email_verified=True,
    )
    whitespace_user = User.objects.create(
        email="spaces@example.com",
        password="not-used",
        username="   ",
        is_email_verified=True,
    )

    new_apps = migrate_state(MIGRATE_TO)
    User = new_apps.get_model("users", "CustomUser")

    assert User.objects.get(pk=null_user.pk).username == "null@example.com"
    assert User.objects.get(pk=empty_user.pk).username == "empty@example.com"
    assert User.objects.get(pk=whitespace_user.pk).username == "spaces@example.com"


def test_backfill_preserves_existing_non_empty_usernames(migrate_state):
    """Pre-existing usernames should remain unchanged during rollout."""

    old_apps = migrate_state(MIGRATE_FROM)
    User = old_apps.get_model("users", "CustomUser")

    preserved_user = User.objects.create(
        email="legacy@example.com",
        password="not-used",
        username="legacy_name",
        is_email_verified=True,
    )

    new_apps = migrate_state(MIGRATE_TO)
    User = new_apps.get_model("users", "CustomUser")

    migrated_user = User.objects.get(pk=preserved_user.pk)
    assert migrated_user.username == "legacy_name"


def test_backfill_resolves_case_insensitive_email_username_collisions(migrate_state):
    """Backfill should generate a deterministic fallback when email clashes."""

    old_apps = migrate_state(MIGRATE_FROM)
    User = old_apps.get_model("users", "CustomUser")

    User.objects.create(
        email="owner@example.com",
        password="not-used",
        username="taken@example.com",
        is_email_verified=True,
    )
    colliding_user = User.objects.create(
        email="Taken@example.com",
        password="not-used",
        username=None,
        is_email_verified=True,
    )

    new_apps = migrate_state(MIGRATE_TO)
    User = new_apps.get_model("users", "CustomUser")

    migrated_user = User.objects.get(pk=colliding_user.pk)
    assert migrated_user.username == f"Taken@example.com__legacy_{colliding_user.pk}"
