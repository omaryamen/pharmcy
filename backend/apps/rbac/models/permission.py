"""Permission catalog — every capability the platform exposes.

Permissions are a global (non-tenant) registry: a code is a stable API
contract that business modules reference in their authorization layer.
``scope`` marks whether the capability is exercised inside a tenant
(``tenant``) or only at the platform level (``platform``).
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import AuditBase, UUIDTimeStampedModel


class PermissionScope(models.TextChoices):
    PLATFORM = "platform", _("Platform")
    TENANT = "tenant", _("Tenant")


class Permission(UUIDTimeStampedModel, AuditBase):
    code = models.CharField(max_length=150, unique=True, db_index=True, verbose_name="Code")
    name = models.CharField(max_length=150, verbose_name="Name")
    description = models.TextField(blank=True, default="", verbose_name="Description")
    module = models.CharField(max_length=100, db_index=True, verbose_name="Module")
    category = models.CharField(max_length=100, default="general", verbose_name="Category")
    action = models.CharField(max_length=50, verbose_name="Action")
    scope = models.CharField(
        max_length=20,
        choices=PermissionScope.choices,
        default=PermissionScope.TENANT,
        db_index=True,
        verbose_name="Scope",
    )
    is_system = models.BooleanField(default=False, verbose_name="System")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="Active")

    class Meta:
        ordering = ["module", "category", "code"]
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        indexes = [
            models.Index(fields=["module", "category"], name="rbac_perm_module_cat_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.code} ({self.name})"
