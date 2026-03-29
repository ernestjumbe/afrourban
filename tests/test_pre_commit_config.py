"""Repository-level tests for pre-commit workflow configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

PRE_COMMIT_CONFIG_PATH = Path(__file__).resolve().parent.parent / ".pre-commit-config.yaml"
README_PATH = Path(__file__).resolve().parent.parent / "README.md"
EXPECTED_HOOK_IDS = ("backend-ruff", "backend-mypy", "backend-pytest")
EXPECTED_COMMANDS = {
    "backend-ruff": "poetry run ruff check .",
    "backend-mypy": "poetry run mypy .",
    "backend-pytest": "poetry run pytest",
}


def _load_pre_commit_config() -> dict[str, Any]:
    return yaml.safe_load(PRE_COMMIT_CONFIG_PATH.read_text())


def _read_readme() -> str:
    return README_PATH.read_text()


def _backend_hooks_by_id() -> dict[str, dict[str, Any]]:
    config = _load_pre_commit_config()
    hooks: dict[str, dict[str, Any]] = {}

    for repo in config["repos"]:
        for hook in repo.get("hooks", []):
            hooks[hook["id"]] = hook

    return hooks


def _ordered_backend_hook_ids() -> list[str]:
    config = _load_pre_commit_config()

    return [
        hook["id"]
        for repo in config["repos"]
        for hook in repo.get("hooks", [])
    ]


def test_pre_commit_config_defines_required_backend_hooks():
    hooks = _backend_hooks_by_id()

    assert set(hooks) >= set(EXPECTED_HOOK_IDS)


def test_backend_hooks_run_at_pre_commit_stage():
    hooks = _backend_hooks_by_id()

    for hook_id in EXPECTED_HOOK_IDS:
        assert hooks[hook_id]["stages"] == ["pre-commit"]


def test_backend_hooks_use_poetry_backed_repository_scoped_commands():
    hooks = _backend_hooks_by_id()

    for hook_id, command in EXPECTED_COMMANDS.items():
        hook = hooks[hook_id]

        assert hook["entry"] == command
        assert hook["language"] == "system"
        assert hook["pass_filenames"] is False


def test_pre_commit_config_uses_shared_default_stage_and_stable_hook_order():
    config = _load_pre_commit_config()

    assert config["default_stages"] == ["pre-commit"]
    assert _ordered_backend_hook_ids() == list(EXPECTED_HOOK_IDS)


def test_readme_documents_install_and_enablement_steps():
    readme = _read_readme()

    assert "poetry install" in readme
    assert "poetry run pre-commit install" in readme


def test_readme_documents_verification_and_retry_guidance():
    readme = " ".join(_read_readme().lower().split())

    assert "poetry run pre-commit run --all-files" in readme
    assert "after fixing" in readme
    assert "git commit" in readme


def test_readme_documents_shared_three_hook_workflow_expectations():
    readme = " ".join(_read_readme().lower().split())

    assert "same three backend quality gates" in readme
    assert "in this order" in readme
    assert "every contributor" in readme
