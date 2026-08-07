"""App configuration for Branch Management module."""

from __future__ import annotations

from django.apps import AppConfig


class BranchesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.branches"
    verbose_name = "Branch Management"

    def ready(self) -> None:
        try:
            import apps.branches.signals  # noqa: F401
        except ImportError:
            pass
