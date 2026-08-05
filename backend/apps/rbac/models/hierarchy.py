"""Role inheritance edges.

``child_role`` inherits the effective permissions of ``parent_role``. A role
may declare many parents and many children. Direct role-permission links
always override anything inherited (see ``engine.resolver``), and cycles are
rejected at the service layer.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import AuditBase, UUIDTimeStampedModel


class RoleHierarchy(UUIDTimeStampedModel, AuditBase):
    child_role = models.ForeignKey(
        "rbac.Role",
        on_delete=models.CASCADE,
        related_name="parent_links",
        verbose_name="Child role",
    )
    parent_role = models.ForeignKey(
        "rbac.Role",
        on_delete=models.CASCADE,
        related_name="child_links",
        verbose_name="Parent role",
    )

    class Meta:
        ordering = ["child_role", "parent_role"]
        verbose_name = "Role hierarchy"
        verbose_name_plural = "Role hierarchy"
        constraints = [
            models.UniqueConstraint(fields=["child_role", "parent_role"], name="rbac_hierarchy_child_parent_uniq"),
        ]

    def __str__(self) -> str:
        return f"{self.child_role.code} inherits {self.parent_role.code}"
