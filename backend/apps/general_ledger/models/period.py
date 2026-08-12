"""AccountingPeriod domain model."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.general_ledger.models.enums import PeriodStatus


class AccountingPeriod(TenantAwareModel, FullAuditModel):
    """Fiscal accounting period controlling posting locks."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="accounting_periods",
        verbose_name=_("Company"),
        db_index=True,
    )
    fiscal_year = models.PositiveIntegerField(verbose_name=_("Fiscal Year"), db_index=True)
    period_number = models.PositiveSmallIntegerField(verbose_name=_("Period Number (1-12)"), db_index=True)

    name = models.CharField(max_length=50, verbose_name=_("Period Name (e.g. 2026-01)"))
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(verbose_name=_("End Date"))

    status = models.CharField(
        max_length=20,
        choices=PeriodStatus.choices,
        default=PeriodStatus.OPEN,
        db_index=True,
        verbose_name=_("Period Status"),
    )

    class Meta:
        db_table = "gl_accounting_periods"
        verbose_name = _("Accounting Period")
        verbose_name_plural = _("Accounting Periods")
        ordering = ["fiscal_year", "period_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "company", "fiscal_year", "period_number"],
                name="gl_period_tenant_company_yr_num_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} [{self.status}]"
