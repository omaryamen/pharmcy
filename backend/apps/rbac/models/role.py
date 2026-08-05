"""Role and role-permission link.

A role is a tenant-scoped bundle of permissions. Granting and denying happen
on the same ``RolePermission`` link: ``allow=True`` grants the code,
``allow=False`` is an explicit denial that overrides inherited grants within
the same role.
"""

from __future__ import annotations

from django.db import models

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel

from ..managers import TenantSoftDeleteManager


class Role(FullAuditModel, TenantAwareModel):
    name = models.CharField(max_length=150, verbose_name="Name")
    code = models.CharField(max_length=100, verbose_name="Code")
    description = models.TextField(blank=True, default="", verbose_name="Description")
    is_protected = models.BooleanField(default=False, db_index=True, verbose_name="Protected")
    is_default = models.BooleanField(default=False, db_index=True, verbose_name="Default")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="Active")

    permissions = models.ManyToManyField(
        "rbac.Permission",
        through="rbac.RolePermission",
        through_fields=("role", "permission"),
        related_name="roles",
        verbose_name="Permissions",
    )
    parents = models.ManyToManyField(
        "self",
        through="rbac.RoleHierarchy",
        symmetrical=False,
        through_fields=("child_role", "parent_role"),
        related_name="children",
        verbose_name="Parent roles",
    )

    objects = TenantSoftDeleteManager()

    class Meta:
        ordering = ["name"]
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code"], name="rbac_role_tenant_code_uniq"),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class RolePermission(FullAuditModel):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="permission_links", verbose_name="Role")
    permission = models.ForeignKey(
        "rbac.Permission",
        on_delete=models.CASCADE,
        related_name="role_links",
        verbose_name="Permission",
    )
    allow = models.BooleanField(default=True, verbose_name="Allow")

    class Meta:
        ordering = ["role", "permission"]
        verbose_name = "Role permission"
        verbose_name_plural = "Role permissions"
        constraints = [
            models.UniqueConstraint(fields=["role", "permission"], name="rbac_roleperm_role_perm_uniq"),
        ]

    def __str__(self) -> str:
        verb = "allow" if self.allow else "deny"
        return f"{self.role.code} {verb} {self.permission.code}"
