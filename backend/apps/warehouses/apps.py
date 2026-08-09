"""App configuration for Enterprise Warehouse Management module."""

from __future__ import annotations

from django.apps import AppConfig


class WarehousesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.warehouses"
    verbose_name = "Enterprise Warehouse & Storage Location Management"

    def ready(self) -> None:
        try:
            import apps.warehouses.signals  # noqa: F401
        except ImportError:
            pass
