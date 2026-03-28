"""Validate API deprecation policy registry."""

from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from afrourban.api_governance import (
    DEFAULT_DEPRECATION_REGISTRY_PATH,
    DeprecationPolicyError,
    load_and_validate_deprecation_registry,
)


class Command(BaseCommand):
    """Validate docs/api/deprecations.yaml against governance rules."""

    help = "Validate API deprecation metadata and notice window requirements."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--path",
            default=str(DEFAULT_DEPRECATION_REGISTRY_PATH),
            help="Path to deprecation registry YAML file.",
        )

    def handle(self, *args, **options) -> None:
        path = Path(options["path"]).expanduser()

        try:
            load_and_validate_deprecation_registry(path=path)
        except FileNotFoundError as exc:
            raise CommandError(f"Deprecation registry not found: {path}") from exc
        except DeprecationPolicyError as exc:
            raise CommandError(f"Deprecation policy validation failed: {exc}") from exc

        self.stdout.write(
            self.style.SUCCESS(f"Deprecation registry is valid: {path}")
        )
