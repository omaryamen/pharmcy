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
from ..models import Permission, PermissionScope, Role, RolePermission
from ..repositories import RoleAuditLogRepository, RoleRepository, RoleVersionRepository


class RoleBootstrapService:
    def __init__(self) -> None:
        self.role_repository = RoleRepository()
        self.audit_repository = RoleAuditLogRepository()
        self.version_repository = RoleVersionRepository()

    @transaction.atomic
    def ensure_tenant_defaults(self, tenant) -> dict:
        """Create ``admin`` + ``member`` for the tenant if missing.

        Idempotent: existing roles (even soft-deleted ones) are reused and
        restored rather than duplicated, so re-provisioning is always safe.
        """
        created = {"admin": False, "member": False}

        admin, admin_created = self._get_or_restore(
            tenant,
            ADMIN_ROLE_CODE,
            name="Administrator",
            description="Tenant administrator with full access.",
            is_protected=True,
            is_default=False,
        )
        if admin_created:
            self._grant(admin, PermissionScope.TENANT)
            self._snapshot(admin, "bootstrap admin role")
            created["admin"] = True

        member, member_created = self._get_or_restore(
            tenant,
            MEMBER_ROLE_CODE,
            name="Member",
            description="Default role for new tenant members.",
            is_protected=False,
            is_default=True,
        )
        if member_created:
            self._grant(member, PermissionScope.TENANT, actions={"read"}, exclude_modules={"rbac"})
            self._snapshot(member, "bootstrap member role")
            created["member"] = True

        PermissionCache().invalidate()
        return created

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _get_or_restore(self, tenant, code: str, **defaults) -> tuple[Role, bool]:
        """Return (role, was_created). A soft-deleted role is restored in place."""
        role = Role.objects.all_with_deleted().filter(tenant=tenant, code=code).first()
        if role is not None:
            if role.is_deleted:
                role.is_deleted = False
                role.deleted_at = None
                role.save(update_fields=["is_deleted", "deleted_at", "updated_at"])
            return role, False
        role = self.role_repository.create(tenant=tenant, code=code, is_active=True, **defaults)
        return role, True

    def _grant(
        self, role: Role, scope: str, actions: set[str] | None = None, exclude_modules: set[str] | None = None
    ) -> None:
        qs = Permission.objects.filter(is_active=True, scope=scope)
        if actions is not None:
            qs = qs.filter(action__in=actions)
        if exclude_modules:
            qs = qs.exclude(module__in=exclude_modules)
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
