"""EmployeeExpense reimbursement model."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.expenses.models.enums import ReimbursementStatus


class EmployeeExpense(TenantAwareModel, FullAuditModel):
    """Claim and reimbursement tracker for employee-incurred out-of-pocket expenses."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="employee_expense_claims",
        verbose_name=_("Company"),
        db_index=True,
    )
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reimbursement_claims",
        verbose_name=_("Employee"),
        db_index=True,
    )
    expense = models.ForeignKey(
        "expenses.Expense",
        on_delete=models.CASCADE,
        related_name="employee_claims",
        verbose_name=_("Expense Header"),
    )

    claim_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Claim Code (EEX)"))
    claim_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Claimed Amount"))
    approved_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Approved Amount"))
    reimbursed_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Reimbursed Amount"))
    remaining_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Remaining Unsettled Balance"))

    status = models.CharField(
        max_length=25,
        choices=ReimbursementStatus.choices,
        default=ReimbursementStatus.DRAFT,
        db_index=True,
        verbose_name=_("Claim Status"),
    )

    payment_reference = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Settlement Reference"))
    reimbursed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Reimbursed At"))

    class Meta:
        db_table = "employee_expenses"
        verbose_name = _("Employee Expense Claim")
        verbose_name_plural = _("Employee Expense Claims")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "claim_number"],
                name="eex_tenant_number_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.claim_number} - {self.employee.get_full_name()} (${self.claim_amount})"
