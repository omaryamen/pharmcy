"""Expense and ExpenseLine domain models."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.expenses.models.enums import ExpenseStatus, PaymentMethod


class Expense(TenantAwareModel, FullAuditModel):
    """Authoritative expense header representing an operational cost commitment or expenditure."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="expenses",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="expenses",
        null=True,
        blank=True,
        verbose_name=_("Branch Scope"),
    )
    category = models.ForeignKey(
        "expenses.ExpenseCategory",
        on_delete=models.PROTECT,
        related_name="expenses",
        verbose_name=_("Expense Category"),
    )
    expense_request = models.ForeignKey(
        "expenses.ExpenseRequest",
        on_delete=models.SET_NULL,
        related_name="expenses",
        null=True,
        blank=True,
        verbose_name=_("Linked Pre-Approval Request"),
    )
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="employee_expenses",
        null=True,
        blank=True,
        verbose_name=_("Claiming Employee / User"),
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.SET_NULL,
        related_name="expenses",
        null=True,
        blank=True,
        verbose_name=_("Vendor / Supplier"),
    )

    expense_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Expense Number (EXP)"))
    expense_date = models.DateField(default=timezone.now, db_index=True, verbose_name=_("Expense Date"))
    due_date = models.DateField(null=True, blank=True, verbose_name=_("Due Date"))

    department_name = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Department"))
    cost_center_code = models.CharField(max_length=50, blank=True, default="", verbose_name=_("Cost Center Code"))

    description = models.TextField(verbose_name=_("Expense Description"))

    subtotal = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Subtotal"))
    tax_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Tax Amount"))
    discount_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Discount Amount"))
    total_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Total Amount"))

    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal("1.000000"), verbose_name=_("Exchange Rate to Base Currency"))
    base_total_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Base Currency Total"))

    payment_method = models.CharField(
        max_length=30,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH,
        verbose_name=_("Settlement Method"),
    )
    payment_status = models.CharField(max_length=20, default="unpaid", db_index=True, verbose_name=_("Payment Status (unpaid, partially_paid, paid)"))
    approval_status = models.CharField(
        max_length=25,
        choices=ExpenseStatus.choices,
        default=ExpenseStatus.DRAFT,
        db_index=True,
        verbose_name=_("Approval Status"),
    )
    accounting_status = models.CharField(max_length=20, default="draft", db_index=True, verbose_name=_("Accounting Status (draft, posted)"))

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_expenses",
        null=True,
        blank=True,
        verbose_name=_("Approved By"),
    )
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="posted_expenses",
        null=True,
        blank=True,
        verbose_name=_("Posted By"),
    )

    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Approved At"))
    posted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Posted At"))

    class Meta:
        db_table = "expenses"
        verbose_name = _("Expense Record")
        verbose_name_plural = _("Expense Records")
        ordering = ["-expense_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "expense_number"],
                name="exp_tenant_number_uniq",
            )
        ]

    def recalculate_totals(self) -> None:
        """Calculate line subtotals and totals."""
        base_sub = sum((line.total_amount for line in self.lines.all()), Decimal("0.0000"))
        self.subtotal = base_sub
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        self.base_total_amount = self.total_amount * self.exchange_rate

    def __str__(self) -> str:
        return f"{self.expense_number} [{self.category.name}] - ${self.total_amount}"


class ExpenseLine(TenantAwareModel, FullAuditModel):
    """Line item detailing specific expense items, tax, GL account, and cost center breakdown."""

    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name=_("Expense Header"),
    )
    category = models.ForeignKey(
        "expenses.ExpenseCategory",
        on_delete=models.PROTECT,
        related_name="lines",
        verbose_name=_("Category"),
    )
    gl_account = models.ForeignKey(
        "general_ledger.ChartOfAccount",
        on_delete=models.SET_NULL,
        related_name="expense_lines",
        null=True,
        blank=True,
        verbose_name=_("Specific GL Account"),
    )

    description = models.CharField(max_length=255, verbose_name=_("Line Description"))
    quantity = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal("1.0000"), verbose_name=_("Quantity"))
    unit_cost = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Unit Cost"))

    subtotal = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Subtotal"))
    tax_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Tax Amount"))
    discount_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Discount Amount"))
    total_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Total Amount"))

    department_name = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Department"))
    cost_center_code = models.CharField(max_length=50, blank=True, default="", verbose_name=_("Cost Center"))

    notes = models.TextField(blank=True, default="", verbose_name=_("Line Notes"))

    class Meta:
        db_table = "expense_lines"
        verbose_name = _("Expense Line")
        verbose_name_plural = _("Expense Lines")

    def save(self, *args, **kwargs) -> None:
        self.subtotal = self.quantity * self.unit_cost
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        super().save(*args, **kwargs)
