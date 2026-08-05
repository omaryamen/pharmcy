"""Permission catalog service.

Keeps the catalog in sync with code constants (``sync_catalog``), validates
the code format, and protects system permissions from destructive changes.
"""

from __future__ import annotations

import re

from django.conf import settings

from apps.common.exceptions import ConflictError, NotFoundError
from apps.common.services.base import BaseService
from apps.common.utils.context import get_current_user

from ..constants import PERMISSION_CATALOG, RBAC_PERMISSIONS
from ..engine.cache import PermissionCache
from ..exceptions import InvalidPermissionCodeError, PermissionInUseError, ProtectedPermissionError
from ..models import Permission
from ..repositories import PermissionRepository

CODE_REGEX = re.compile(settings.RBAC_PERMISSION_CODE_REGEX)


class PermissionService(BaseService[Permission]):
    model = Permission
    repository_class = PermissionRepository

    def create(self, data: dict) -> Permission:
        self._assert_actor_can(RBAC_PERMISSIONS["PERMISSION_CREATE"])
        payload = dict(data)
        payload["code"] = payload.get("code", "").strip().lower()
        self._validate_code(payload.get("code", ""))
        if self.repository.exists(code=payload["code"]):
            raise ConflictError(f"A permission with code '{payload['code']}' already exists.")
        permission = self.repository.create(**payload)
        PermissionCache().invalidate()
        return permission

    def update(self, id, data: dict) -> Permission:
        instance = self.get(id)
        self._assert_actor_can(RBAC_PERMISSIONS["PERMISSION_UPDATE"])
        payload = dict(data)
        if "code" in payload:
            payload["code"] = payload["code"].strip().lower()
            self._validate_code(payload["code"])
            if instance.is_system and payload["code"] != instance.code:
                raise ProtectedPermissionError()
            if payload["code"] != instance.code and self.repository.exists(code=payload["code"]):
                raise ConflictError(f"A permission with code '{payload['code']}' already exists.")
        if instance.is_system:
            if "scope" in payload and payload["scope"] != instance.scope:
                raise ProtectedPermissionError()
            if "is_system" in payload and payload["is_system"] is False:
                raise ProtectedPermissionError()
        permission = self.repository.update(instance, **payload)
        PermissionCache().invalidate()
        return permission

    def delete(self, id) -> Permission:
        instance = self.get(id)
        self._assert_actor_can(RBAC_PERMISSIONS["PERMISSION_DELETE"])
        if instance.is_system:
            raise ProtectedPermissionError()
        if instance.role_links.exists() or instance.user_overrides.exists():
            raise PermissionInUseError()
        permission = self.repository.delete(instance)
        PermissionCache().invalidate()
        return permission

    # ------------------------------------------------------------------
    # Catalog reconciliation
    # ------------------------------------------------------------------
    def sync_catalog(self, catalog: list[dict] | None = None) -> dict:
        """Reconcile the database catalog with the code catalog.

        Creates missing permissions, refreshes metadata, and deactivates
        catalog entries that no longer exist in code. Idempotent; safe to run
        on every deploy.
        """
        entries = catalog if catalog is not None else PERMISSION_CATALOG
        expected_codes = {entry["code"] for entry in entries}
        created = updated = 0

        for entry in entries:
            _obj, was_created = self.repository.update_or_create(
                defaults={
                    "name": entry["name"],
                    "description": entry.get("description", ""),
                    "module": entry["module"],
                    "category": entry["category"],
                    "action": entry["action"],
                    "scope": entry["scope"],
                    "is_system": True,
                    "is_active": True,
                },
                code=entry["code"],
            )
            if was_created:
                created += 1
            else:
                updated += 1

        deactivated = self.repository.filter(is_active=True).exclude(code__in=expected_codes).update(is_active=False)

        PermissionCache().invalidate()
        return {"created": created, "updated": updated, "deactivated": deactivated, "total": len(entries)}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _validate_code(self, code: str) -> None:
        if not code or not CODE_REGEX.match(code):
            raise InvalidPermissionCodeError()

    def _assert_actor_can(self, code: str) -> None:
        from ..engine import PermissionEngine

        actor = get_current_user()
        if actor is None or actor.is_superuser or not getattr(actor, "is_authenticated", True):
            return
        from apps.common.utils.context import get_current_tenant

        if not PermissionEngine().has_permission(actor, code, get_current_tenant()):
            from ..exceptions import MissingRbacPermissionError

            raise MissingRbacPermissionError(f"Permission '{code}' is required.")
