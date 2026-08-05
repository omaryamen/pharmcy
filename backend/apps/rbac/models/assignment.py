"""User → role assignment and per-user permission overrides.

Assignments are tenant-scoped: the same user can hold different roles in
different tenants. Overrides are the highest-priority source in the engine —
an explicit user-level allow/deny beats every role (including inherited)
decision for that code.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel

from ..managers import TenantSoftDeleteManager


class UserRoleAssignment(FullAuditModel, TenantAwareModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="role_assignments",
        verbose_name="User",
    )
    role = models.ForeignKey(
        "rbac.Role",
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name="Role",
    )
    is_primary = models.BooleanField(default=False, verbose_name="Primary role")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="Active")
    reason = models.CharField(max_length=255, blank=True, default="", verbose_name="Reason")

    objects = TenantSoftDeleteManager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "User role assignment"
        verbose_name_plural = "User role assignments"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "user", "role"], name="rbac_assignment_tenant_user_role_uniq"),
        ]

    def __str__(self) -> str:
        return f"{self.user} → {self.role.code}"

    @property
    def assigned_by(self):
        return self.created_by


class UserPermissionOverride(FullAuditModel, TenantAwareModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="permission_overrides",
        verbose_name="User",
    )
    permission = models.ForeignKey(
        "rbac.Permission",
        on_delete=models.CASCADE,
        related_name="user_overrides",
        verbose_name="Permission",
    )
    allow = models.BooleanField(default=True, verbose_name="Allow")

    objects = TenantSoftDeleteManager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "User permission override"
        verbose_name_plural = "User permission overrides"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "user", "permission"], name="rbac_override_tenant_user_perm_uniq"
            ),
        ]

    def __str__(self) -> str:
        verb = "allow" if self.allow else "deny"
        return f"{self.user} {verb} {self.permission.code}"
