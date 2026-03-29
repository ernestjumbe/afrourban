# afrourban Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-29

## Active Technologies
- Python 3.11 (project constraint `^3.11`) + Django 5.1.2, Django REST Framework, SimpleJWT, drf-spectacular, structlog (006-add-username-privacy)
- Django ORM on PostgreSQL (production) / SQLite (dev+test), with new user-field migration (006-add-username-privacy)
- Python 3.11 (project constraint `^3.11`) + Django 5.1.2, Django REST Framework 3.17.1, drf-spectacular 0.29.0, structlog, SimpleJWT (existing project auth stack) (007-health-endpoint)
- Existing PostgreSQL (production) / SQLite (dev+test); no new persistent tables or migrations required (007-health-endpoint)
- Python 3.11 (project constraint `^3.11`) + Django 5.1.2, Poetry, pytest, Ruff, mypy, plus new `pre-commit` dev dependency (008-backend-precommit-hooks)

- Python 3.11 + Django 5.1.2, Django REST Framework, SimpleJWT, drf-spectacular, structlog (005-api-url-versioning-docs)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.11: Follow standard conventions

## Recent Changes
- 008-backend-precommit-hooks: Added Python 3.11 (project constraint `^3.11`) + Django 5.1.2, Poetry, pytest, Ruff, mypy, plus new `pre-commit` dev dependency
- 007-health-endpoint: Added Python 3.11 (project constraint `^3.11`) + Django 5.1.2, Django REST Framework 3.17.1, drf-spectacular 0.29.0, structlog, SimpleJWT (existing project auth stack)
- 006-add-username-privacy: Added Python 3.11 (project constraint `^3.11`) + Django 5.1.2, Django REST Framework, SimpleJWT, drf-spectacular, structlog


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
