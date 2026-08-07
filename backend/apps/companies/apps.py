"""App configuration for Company Management module."""

from __future__ import annotations

from django.apps import AppConfig


class CompaniesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.companies"
    verbose_name = "Company Management"

    def ready(self) -> None:
        try:
            import apps.companies.signals  # noqa: F401
        except ImportError:
            pass
