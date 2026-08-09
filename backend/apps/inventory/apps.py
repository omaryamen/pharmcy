"""App configuration for Enterprise Inventory & Batch Management module."""

from __future__ import annotations

from django.apps import AppConfig


class InventoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.inventory"
    verbose_name = "Enterprise Inventory & Batch Management"

    def ready(self) -> None:
        try:
            import apps.inventory.signals  # noqa: F401
        except ImportError:
            pass
