"""App configuration for Enterprise Customer Management module."""

from __future__ import annotations

from django.apps import AppConfig


class CustomersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.customers"
    verbose_name = "Enterprise Customer Management"

    def ready(self) -> None:
        try:
            import apps.customers.signals  # noqa: F401
        except ImportError:
            pass
