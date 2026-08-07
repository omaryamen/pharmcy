"""App configuration for Tenant Management module."""

from __future__ import annotations

from django.apps import AppConfig


class TenantsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.tenants"
    verbose_name = "Tenant Management"

    def ready(self) -> None:
        try:
            import apps.tenants.signals  # noqa: F401
        except ImportError:
            pass
