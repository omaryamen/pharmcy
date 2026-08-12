"""ExpenseReversal and ExpenseAdjustment domain models."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel


class ExpenseReversal(TenantAwareModel, FullAuditModel):
    """Audit record for immutable reversal of posted expenses via compensating GL journals."""

    expense = models.ForeignKey(
        "expenses.Expense",
        on_delete=models.CASCADE,
        related_name="reversals",
        verbose_name=_("Original Expense Header"),
    )

    reversal_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Reversal Number (EXV)"))
    reversal_date = models.DateField(default=timezone.now, verbose_name=_("Reversal Date"))
    reason = models.TextField(verbose_name=_("Reversal Reason"))

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_expense_reversals",
        null=True,
        blank=True,
        verbose_name=_("Approved By"),
    )

    class Meta:
        db_table = "expense_reversals"
        verbose_name = _("Expense Reversal")
        verbose_name_plural = _("Expense Reversals")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "reversal_number"],
                name="exv_tenant_number_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.reversal_number} -> {self.expense.expense_number}"


class ExpenseAdjustment(TenantAwareModel, FullAuditModel):
    """Audit record for controlled financial adjustments to posted expenses."""

    expense = models.ForeignKey(
        "expenses.Expense",
        on_delete=models.CASCADE,
        related_name="adjustments",
        verbose_name=_("Expense Header"),
    )

    adjustment_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Adjustment Number (EXA)"))
    adjustment_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Adjustment Amount (+/-)"))
    reason = models.TextField(verbose_name=_("Adjustment Reason"))

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_expense_adjustments",
        null=True,
        blank=True,
        verbose_name=_("Approved By"),
    )

    class Meta:
        db_table = "expense_adjustments"
        verbose_name = _("Expense Adjustment")
        verbose_name_plural = _("Expense Adjustments")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "adjustment_number"],
                name="exa_tenant_number_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.adjustment_number} (${self.adjustment_amount}) -> {self.expense.expense_number}"
