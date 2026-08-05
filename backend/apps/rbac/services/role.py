"""Role lifecycle service.

Owns role CRUD, permission-set replacement, cloning, versioned history and
the protected-role guard. Every mutating operation records a version snapshot
and an audit-log entry and invalidates the effective-permission cache.
"""

from __future__ import annotations

import re

from django.conf import settings
from django.db import transaction

from apps.common.exceptions import ConflictError
from apps.common.services.base import BaseService
from apps.common.utils.context import get_current_tenant, get_current_user

from ..constants import PROTECTED_ROLE_CODES, RBAC_PERMISSIONS
from ..engine import PermissionCache, PermissionEngine
from ..exceptions import MissingRbacPermissionError, ProtectedRoleError, RoleInUseError
from ..models import Permission, Role, RoleHierarchy
from ..repositories import (
    RoleAuditLogRepository,
    RolePermissionRepository,
    RoleRepository,
    RoleVersionRepository,
)

CODE_REGEX = re.compile(r"^[a-z][a-z0-9_]*$")


class RoleService(BaseService[Role]):
    model = Role
    repository_class = RoleRepository

    def __init__(self, repository: RoleRepository | None = None) -> None:
        super().__init__(repository)
        self.permission_repository = RolePermissionRepository()
        self.audit_repository = RoleAuditLogRepository()
        self.version_repository = RoleVersionRepository()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------
    def history(self, role: Role) -> dict:
        self._assert_can(RBAC_PERMISSIONS["ROLE_READ"], role.tenant)
        return {
            "versions": list(self.version_repository.snapshots(role)),
            "audit_logs": list(self.audit_repository.for_role(role)),
        }

    def permissions_matrix(self, role: Role) -> dict:
        from ..engine.resolver import PermissionResolver

        self._assert_can(RBAC_PERMISSIONS["ROLE_READ"], role.tenant)
        resolver = PermissionResolver()
        matrix = {}
        for code, (allow, source) in resolver.role_permission_map(role).items():
            matrix[code] = {"allow": allow, "source": source}
        return matrix

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------
    @transaction.atomic
    def create(self, data: dict) -> Role:
        payload = dict(data)
        if payload.get("tenant") is None:
            current = get_current_tenant()
            if current is not None:
                payload["tenant"] = current
        self._validate_create(payload)
        self._assert_can(RBAC_PERMISSIONS["ROLE_CREATE"], payload.get("tenant"))

        actor = self._actor()
        wants_protected = bool(payload.pop("is_protected", False))
        if wants_protected and not self._can_manage_protected(actor, payload.get("tenant")):
            raise ProtectedRoleError()
        payload["is_protected"] = wants_protected and self._can_manage_protected(actor, payload.get("tenant"))

        role = self.repository.create(**payload)
        self._snapshot(role, f"role created ({payload.get('code', '')})")
        self._audit(role, "created", {"fields": sorted(payload.keys())})
        PermissionCache().invalidate()
        return role

    @transaction.atomic
    def update(self, id, data: dict) -> Role:
        role = self.get(id)
        payload = dict(data)
        self._assert_can(RBAC_PERMISSIONS["ROLE_UPDATE"], role.tenant)
        self._assert_role_mutable(role)

        if "code" in payload:
            payload["code"] = payload["code"].strip().lower()
            if role.is_protected and payload["code"] != role.code:
                raise ProtectedRoleError()
            if payload["code"] != role.code and self.repository.exists(tenant=role.tenant, code=payload["code"]):
                raise ConflictError(f"A role with code '{payload['code']}' already exists.")

        if role.is_protected:
            if payload.get("is_protected") is False:
                raise ProtectedRoleError()
        else:
            actor = self._actor()
            payload["is_protected"] = role.is_protected and True
            if payload.get("is_protected") is True and not self._can_manage_protected(actor, role.tenant):
                payload["is_protected"] = False

        role = self.repository.update(role, **payload)
        self._snapshot(role, "role updated")
        self._audit(role, "updated", {"fields": sorted(payload.keys())})
        PermissionCache().invalidate()
        return role

    @transaction.atomic
    def delete(self, id) -> Role:
        role = self.get(id)
        self._assert_can(RBAC_PERMISSIONS["ROLE_DELETE"], role.tenant)
        self._assert_role_mutable(role)
        if role.assignments.filter(is_active=True).exists():
            raise RoleInUseError()
        role = self.repository.delete(role)
        self._audit(role, "deleted", {})
        PermissionCache().invalidate()
        return role

    # ------------------------------------------------------------------
    # Permission set replacement
    # ------------------------------------------------------------------
    @transaction.atomic
    def set_permissions(self, role: Role, permission_map: dict[str, bool]) -> None:
        """Replace ``role``'s effective link set with ``{code: allow}``.

        Codes not present in the map are removed from the role. ``allow``
        values are coerced to booleans; unknown codes abort the operation.
        """
        normalized = {code.strip().lower(): bool(allow) for code, allow in permission_map.items()}
        self._assert_can(RBAC_PERMISSIONS["ROLE_UPDATE"], role.tenant)
        self._assert_role_mutable(role)

        codes = list(normalized.keys())
        known = set(Permission.objects.filter(code__in=codes, is_active=True).values_list("code", flat=True))
        unknown = set(codes) - known
        if unknown:
            raise ConflictError(f"Unknown or inactive permission codes: {', '.join(sorted(unknown))}")

        self.permission_repository.replace_for_role(role, normalized)
        self._snapshot(role, "permissions updated")
        self._audit(role, "permissions_updated", {"permissions": normalized})
        PermissionCache().invalidate()

    @transaction.atomic
    def clone(self, role: Role, *, name: str, code: str, description: str = "") -> Role:
        """Duplicate a role (links + inheritance) under a new, non-protected identity."""
        self._assert_can(RBAC_PERMISSIONS["ROLE_CREATE"], role.tenant)
        code = code.strip().lower()
        self._validate_code_format(code)
        if self.repository.exists(tenant=role.tenant, code=code):
            raise ConflictError(f"A role with code '{code}' already exists.")

        clone = self.repository.create(
            tenant=role.tenant,
            name=name.strip() or f"{role.name} (copy)",
            code=code,
            description=description,
            is_protected=False,
            is_default=False,
            is_active=True,
        )
        link_map = {
            link.permission.code: link.allow for link in role.permission_links.select_related("permission")
        }
        self.permission_repository.replace_for_role(clone, link_map)
        for parent in role.parent_links.select_related("parent_role"):
            RoleHierarchy.objects.get_or_create(child_role=clone, parent_role=parent.parent_role)

        self._snapshot(clone, f"cloned from {role.code}")
        self._audit(clone, "cloned", {"source": role.code})
        PermissionCache().invalidate()
        return clone

    # ------------------------------------------------------------------
    # Bootstrap-friendly helpers
    # ------------------------------------------------------------------
    def get_or_create_bootstrap_role(self, *, tenant, code: str, name: str, **defaults) -> Role:
        role = self.repository.get_by_code(tenant, code)
        if role is not None:
            return role
        return self.repository.create(tenant=tenant, code=code, name=name, is_active=True, **defaults)

    # ------------------------------------------------------------------
    # Guards
    # ------------------------------------------------------------------
    def _validate_create(self, payload: dict) -> None:
        code = payload.get("code")
        if code is None:
            raise ConflictError("Role 'code' is required.")
        payload["code"] = code.strip().lower()
        self._validate_code_format(payload["code"])
        if payload["code"] in PROTECTED_ROLE_CODES:
            raise ProtectedRoleError(f"'{payload['code']}' is a reserved role code.")
        if not payload.get("name"):
            raise ConflictError("Role 'name' is required.")
        if self.repository.exists(tenant=payload.get("tenant"), code=payload["code"]):
            raise ConflictError(f"A role with code '{payload['code']}' already exists.")

    @staticmethod
    def _validate_code_format(code: str) -> None:
        if not CODE_REGEX.match(code):
            raise ConflictError("Role codes must be lowercase letters, digits and underscores.")

    def _assert_can(self, code: str, tenant) -> None:
        actor = self._actor()
        if actor is None or actor.is_superuser:
            return
        if not PermissionEngine().has_permission(actor, code, tenant):
            raise MissingRbacPermissionError(f"Permission '{code}' is required.")

    def _can_manage_protected(self, actor, tenant) -> bool:
        if actor is None or actor.is_superuser:
            return True
        return PermissionEngine().has_permission(actor, RBAC_PERMISSIONS["ROLE_PROTECTED_MANAGE"], tenant)

    def _assert_role_mutable(self, role: Role) -> None:
        if role.is_protected:
            actor = self._actor()
            if actor is None or actor.is_superuser:
                return
            if not self._can_manage_protected(actor, role.tenant):
                raise ProtectedRoleError()

    def _actor(self):
        user = get_current_user()
        if user is None or not getattr(user, "is_authenticated", False):
            return None
        return user

    # ------------------------------------------------------------------
    # History / audit
    # ------------------------------------------------------------------
    def _snapshot(self, role: Role, reason: str) -> None:
        snapshot = {
            "name": role.name,
            "code": role.code,
            "description": role.description,
            "is_protected": role.is_protected,
            "is_default": role.is_default,
            "is_active": role.is_active,
            "permissions": {
                link.permission.code: link.allow for link in role.permission_links.select_related("permission")
            },
            "parents": list(role.parent_links.values_list("parent_role__code", flat=True)),
        }
        version = self.version_repository.next_version(role)
        self.version_repository.create(
            role=role,
            version=version,
            snapshot=snapshot,
            reason=reason,
            created_by=self._actor(),
        )
        self.version_repository.prune(role, settings.RBAC_ROLE_HISTORY_MAX_VERSIONS)

    def _audit(self, role: Role, action: str, details: dict) -> None:
        actor = self._actor()
        self.audit_repository.record(role=role, action=action, actor=actor, details=details)
