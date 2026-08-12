"""RecurringExpense schedule model."""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.expenses.models.enums import RecurringFrequency


class RecurringExpense(TenantAwareModel, FullAuditModel):
    """Recurring operational expense schedule template."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="recurring_expenses",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="recurring_expenses",
        null=True,
        blank=True,
        verbose_name=_("Branch Scope"),
    )
    category = models.ForeignKey(
        "expenses.ExpenseCategory",
        on_delete=models.PROTECT,
        related_name="recurring_expenses",
        verbose_name=_("Expense Category"),
    )

    name = models.CharField(max_length=150, verbose_name=_("Schedule Name"))
    amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Expense Amount"))
    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))

    frequency = models.CharField(
        max_length=20,
        choices=RecurringFrequency.choices,
        default=RecurringFrequency.MONTHLY,
        db_index=True,
        verbose_name=_("Recurrence Frequency"),
    )

    start_date = models.DateField(default=timezone.now, verbose_name=_("Start Date"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("End Date"))
    next_due_date = models.DateField(db_index=True, verbose_name=_("Next Execution Due Date"))

    auto_generate = models.BooleanField(default=True, verbose_name=_("Auto-Generate Expense Record"))
    auto_post = models.BooleanField(default=False, verbose_name=_("Auto-Post to GL if Approved"))
    status = models.CharField(max_length=20, default="active", db_index=True, verbose_name=_("Status (active, paused, cancelled)"))

    class Meta:
        db_table = "recurring_expenses"
        verbose_name = _("Recurring Expense Schedule")
        verbose_name_plural = _("Recurring Expense Schedules")
        ordering = ["next_due_date"]

    def __str__(self) -> str:
        return f"{self.name} [{self.frequency}] - ${self.amount}"
