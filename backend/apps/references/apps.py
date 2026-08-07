"""App configuration for Enterprise Pharmaceutical Reference Data module."""

from __future__ import annotations

from django.apps import AppConfig


class ReferencesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.references"
    verbose_name = "Enterprise Pharmaceutical Reference Data"

    def ready(self) -> None:
        try:
            import apps.references.signals  # noqa: F401
        except ImportError:
            pass
