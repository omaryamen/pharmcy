"""Celery application configuration.

Reads every ``CELERY_*`` setting from Django settings (namespace ``CELERY``).
Worker entry-point: ``celery -A config worker -l INFO``.
"""

from __future__ import annotations

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("pharmacloud")

# Read settings from the Django settings module with the CELERY_ namespace.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in each installed app's ``tasks`` module.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self) -> None:
    """Debug task used to verify worker connectivity."""
    print(f"Request: {self.request!r}")
