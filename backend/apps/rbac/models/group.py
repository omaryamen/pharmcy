"""Role group: a named bundle of roles for bulk assignment."""

from __future__ import annotations

from django.db import models

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel

from ..managers import TenantSoftDeleteManager


class RoleGroup(FullAuditModel, TenantAwareModel):
    name = models.CharField(max_length=150, verbose_name="Name")
    code = models.CharField(max_length=100, verbose_name="Code")
    description = models.TextField(blank=True, default="", verbose_name="Description")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="Active")

    roles = models.ManyToManyField(
        "rbac.Role",
        through="rbac.RoleGroupMembership",
        through_fields=("group", "role"),
        related_name="groups",
        verbose_name="Roles",
    )

    objects = TenantSoftDeleteManager()

    class Meta:
        ordering = ["name"]
        verbose_name = "Role group"
        verbose_name_plural = "Role groups"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code"], name="rbac_group_tenant_code_uniq"),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class RoleGroupMembership(FullAuditModel):
    group = models.ForeignKey(RoleGroup, on_delete=models.CASCADE, related_name="memberships", verbose_name="Group")
    role = models.ForeignKey(
        "rbac.Role", on_delete=models.CASCADE, related_name="group_memberships", verbose_name="Role"
    )

    class Meta:
        ordering = ["group", "role"]
        verbose_name = "Role group membership"
        verbose_name_plural = "Role group memberships"
        constraints = [
            models.UniqueConstraint(fields=["group", "role"], name="rbac_groupmem_group_role_uniq"),
        ]

    def __str__(self) -> str:
        return f"{self.group.code} + {self.role.code}"
