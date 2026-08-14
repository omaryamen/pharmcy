"""ReportDefinition domain model for registering platform reports."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.reports.models.enums import ReportCategory


class ReportDefinition(TenantAwareModel, FullAuditModel):
    """Metadata registry of system-supported enterprise reports."""

    code = models.CharField(max_length=60, db_index=True, verbose_name=_("Report Code (e.g. RPT-SAL-001)"))
    name = models.CharField(max_length=150, verbose_name=_("Report Title"))
    category = models.CharField(
        max_length=35,
        choices=ReportCategory.choices,
        default=ReportCategory.SALES,
        db_index=True,
        verbose_name=_("Report Category"),
    )

    description = models.TextField(blank=True, default="", verbose_name=_("Report Description"))
    required_permission = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Required RBAC Permission"))

    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    is_financial = models.BooleanField(default=False, verbose_name=_("Is Authoritative Financial Report"))

    class Meta:
        db_table = "report_definitions"
        verbose_name = _("Report Definition")
        verbose_name_plural = _("Report Definitions")
        ordering = ["category", "code"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "code"],
                name="rpt_def_tenant_code_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name} [{self.category}]"
