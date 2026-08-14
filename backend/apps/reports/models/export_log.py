"""ReportExportLog domain model for audit tracking of report generation and data downloads."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.reports.models.enums import ExportFormat, ReportCategory


class ReportExportLog(TenantAwareModel, FullAuditModel):
    """Audit log recording every execution, view, or file export of derived reporting data."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="report_export_logs",
        verbose_name=_("Company"),
        db_index=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="report_exports",
        null=True,
        blank=True,
        verbose_name=_("Executed By User"),
    )

    report_code = models.CharField(max_length=60, db_index=True, verbose_name=_("Report Code"))
    report_category = models.CharField(
        max_length=35,
        choices=ReportCategory.choices,
        default=ReportCategory.SALES,
        verbose_name=_("Report Category"),
    )

    export_format = models.CharField(
        max_length=20,
        choices=ExportFormat.choices,
        default=ExportFormat.JSON,
        verbose_name=_("Export Format"),
    )

    record_count = models.IntegerField(default=0, verbose_name=_("Exported Record Count"))
    filters_applied = models.JSONField(default=dict, blank=True, verbose_name=_("Filters Criteria Applied"))

    class Meta:
        db_table = "report_export_logs"
        verbose_name = _("Report Export Log")
        verbose_name_plural = _("Report Export Logs")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.report_code} ({self.export_format}) by {self.user} at {self.created_at}"
