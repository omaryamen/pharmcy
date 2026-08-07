"""App configuration for Enterprise Supplier Management module."""

from __future__ import annotations

from django.apps import AppConfig


class SuppliersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.suppliers"
    verbose_name = "Enterprise Supplier Management"

    def ready(self) -> None:
        try:
            import apps.suppliers.signals  # noqa: F401
        except ImportError:
            pass
