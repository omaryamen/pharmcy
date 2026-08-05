"""RBAC app configuration.

``ready`` wires the model signals: tenant bootstrap (default roles created on
tenant creation) and permission-cache invalidation whenever any RBAC graph
edge changes.
"""

from __future__ import annotations

from django.apps import AppConfig


class RbacConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.rbac"
    label = "rbac"
    verbose_name = "Role-Based Access Control"

    def ready(self) -> None:
        from . import signals  # noqa: F401
