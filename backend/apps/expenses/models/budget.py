"""ExpenseBudget fiscal period budget foundation model."""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel


class ExpenseBudget(TenantAwareModel, FullAuditModel):
    """Fiscal budget allocation foundation model per branch, category, and period."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="expense_budgets",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="expense_budgets",
        null=True,
        blank=True,
        verbose_name=_("Branch Scope"),
    )
    category = models.ForeignKey(
        "expenses.ExpenseCategory",
        on_delete=models.CASCADE,
        related_name="budgets",
        verbose_name=_("Expense Category"),
    )

    fiscal_year = models.IntegerField(verbose_name=_("Fiscal Year"))
    period_number = models.IntegerField(default=1, verbose_name=_("Fiscal Period / Month (1-12)"))

    department_name = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Department"))
    cost_center_code = models.CharField(max_length=50, blank=True, default="", verbose_name=_("Cost Center"))

    budget_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Allocated Budget Amount"))
    committed_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Committed Pre-Approved Amount"))
    actual_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Actual Expenditure Amount"))

    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))
    status = models.CharField(max_length=20, default="active", verbose_name=_("Budget Status (active, locked, closed)"))

    class Meta:
        db_table = "expense_budgets"
        verbose_name = _("Expense Budget")
        verbose_name_plural = _("Expense Budgets")
        ordering = ["fiscal_year", "period_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "company", "category", "fiscal_year", "period_number"],
                name="exp_bgt_tenant_cat_yr_prd_uniq",
            )
        ]

    @property
    def available_amount(self) -> Decimal:
        return self.budget_amount - (self.committed_amount + self.actual_amount)

    @property
    def utilization_percentage(self) -> Decimal:
        if self.budget_amount == Decimal("0.0000"):
            return Decimal("0.0000")
        return ((self.committed_amount + self.actual_amount) / self.budget_amount) * Decimal("100.0000")

    def __str__(self) -> str:
        return f"Budget FY{self.fiscal_year}-P{self.period_number} [{self.category.name}]: ${self.budget_amount}"
