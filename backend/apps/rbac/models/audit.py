"""Versioned role history and change audit.

Every mutating operation on a role is recorded twice:

- ``RoleVersion`` keeps a JSON snapshot (permissions + parents) so the role
  can be rolled back or compared at any point in its lifecycle;
- ``RoleAuditLog`` keeps a lightweight, append-only change trail.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import UUIDTimeStampedModel


class RoleVersion(UUIDTimeStampedModel):
    role = models.ForeignKey("rbac.Role", on_delete=models.CASCADE, related_name="versions", verbose_name="Role")
    version = models.PositiveIntegerField(default=1, verbose_name="Version")
    snapshot = models.JSONField(default=dict, verbose_name="Snapshot")
    reason = models.CharField(max_length=255, blank=True, default="", verbose_name="Reason")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="Created by",
    )

    class Meta:
        ordering = ["-version"]
        verbose_name = "Role version"
        verbose_name_plural = "Role versions"
        constraints = [
            models.UniqueConstraint(fields=["role", "version"], name="rbac_roleversion_role_version_uniq"),
        ]

    def __str__(self) -> str:
        return f"{self.role.code} v{self.version}"


class RoleAuditLog(UUIDTimeStampedModel):
    role = models.ForeignKey("rbac.Role", on_delete=models.CASCADE, related_name="audit_logs", verbose_name="Role")
    action = models.CharField(max_length=64, db_index=True, verbose_name="Action")
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="Actor",
    )
    details = models.JSONField(default=dict, verbose_name="Details")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Role audit log"
        verbose_name_plural = "Role audit logs"

    def __str__(self) -> str:
        return f"{self.role.code} {self.action}"
