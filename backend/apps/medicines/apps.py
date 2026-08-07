"""App configuration for Enterprise Medicine Master Data module."""

from __future__ import annotations

from django.apps import AppConfig


class MedicinesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.medicines"
    verbose_name = "Enterprise Medicine Master Data"

    def ready(self) -> None:
        try:
            import apps.medicines.signals  # noqa: F401
        except ImportError:
            pass
