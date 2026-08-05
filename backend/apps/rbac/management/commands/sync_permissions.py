"""Reconcile the permission catalog with the code constants.

Run after adding/renaming permission codes in ``apps.rbac.constants``:

    python manage.py sync_permissions
"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.rbac.services import PermissionService


class Command(BaseCommand):
    help = "Reconcile the permission catalog with the code constants."

    def handle(self, *args, **options) -> None:
        result = PermissionService().sync_catalog()
        self.stdout.write(
            self.style.SUCCESS(
                "Permission catalog synced: "
                f"{result['created']} created, {result['updated']} updated, "
                f"{result['deactivated']} deactivated, {result['total']} total."
            )
        )
