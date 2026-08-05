"""Tenant bootstrap: provision the baseline roles on tenant creation.

Idempotent and safe to call at any time (e.g. from a management command to
repair a tenant). Creates the protected ``admin`` role (all active
tenant-scope permissions) and the default ``member`` role (every read
permission), plus their initial version snapshots.
"""

from __future__ import annotations

from django.db import transaction

from ..constants import ADMIN_ROLE_CODE, MEMBER_ROLE_CODE
from ..engine import PermissionCache
from ..models import Permission, Role, RolePermission, PermissionScope
from ..repositories import RoleAuditLogRepository, RoleRepository, RoleVersionRepository


class RoleBootstrapService:
    def __init__(self) -> None:
        self.role_repository = RoleRepository()
        self.audit_repository = RoleAuditLogRepository()
        self.version_repository = RoleVersionRepository()

    @transaction.atomic
    def ensure_tenant_defaults(self, tenant) -> dict:
        """Create ``admin`` + ``member`` for the tenant if missing."""
        created = {"admin": False, "member": False}

        admin = self.role_repository.get_by_code(tenant, ADMIN_ROLE_CODE)
        if admin is None:
            admin = self.role_repository.create(
                tenant=tenant,
                name="Administrator",
                code=ADMIN_ROLE_CODE,
                description="Tenant administrator with full access.",
                is_protected=True,
                is_default=False,
                is_active=True,
            )
            self._grant(admin, PermissionScope.TENANT)
            self._snapshot(admin, "bootstrap admin role")
            created["admin"] = True

        member = self.role_repository.get_by_code(tenant, MEMBER_ROLE_CODE)
        if member is None:
            member = self.role_repository.create(
                tenant=tenant,
                name="Member",
                code=MEMBER_ROLE_CODE,
                description="Default role for new tenant members.",
                is_protected=False,
                is_default=True,
                is_active=True,
            )
            self._grant(member, PermissionScope.TENANT, actions={"read"})
            self._snapshot(member, "bootstrap member role")
            created["member"] = True

        PermissionCache().invalidate()
        return created

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _grant(self, role: Role, scope: str, actions: set[str] | None = None) -> None:
        qs = Permission.objects.filter(is_active=True, scope=scope)
        if actions is not None:
            qs = qs.filter(action__in=actions)
        links = [RolePermission(role=role, permission=permission, allow=True) for permission in qs]
        RolePermission.objects.bulk_create(links, batch_size=500)

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
            "parents": [],
        }
        self.version_repository.create(
            role=role,
            version=1,
            snapshot=snapshot,
            reason=reason,
            created_by=None,
        )
        self.audit_repository.record(role=role, action="bootstrap_created", actor=None, details={"reason": reason})
