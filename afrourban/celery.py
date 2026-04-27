"""
Celery configuration for Zimzimba platform.

This module contains the Celery application instance and configuration.
"""

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "afrourban.settings.local")

app = Celery("afrourban")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat schedule (T017)
app.conf.beat_schedule = {
    "cleanup-expired-login-sessions": {
        "task": "authentication.cleanup_expired_login_sessions",
        "schedule": 1800.0,  # Every 30 minutes (in seconds)
        "options": {
            "expires": 300,  # Task expires after 5 minutes if not picked up
        },
    },
}
