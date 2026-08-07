"""App configuration for Enterprise User Management module."""

from __future__ import annotations

from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"
    verbose_name = "Enterprise User Management"

    def ready(self) -> None:
        try:
            import apps.users.signals  # noqa: F401
        except ImportError:
            pass
