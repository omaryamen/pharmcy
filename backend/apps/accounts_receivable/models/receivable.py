"""CustomerReceivable subledger domain model."""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.accounts_receivable.models.enums import ARStatus
from apps.common.models import FullAuditModel, TenantAwareModel


class CustomerReceivable(TenantAwareModel, FullAuditModel):
    """Subledger record tracking individual customer financial obligations created by POS sales, credit sales, or manual entries."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="customer_receivables",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="customer_receivables",
        null=True,
        blank=True,
        verbose_name=_("Branch"),
        db_index=True,
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="customer_receivables",
        verbose_name=_("Customer / Client"),
        db_index=True,
    )
    sales_invoice = models.ForeignKey(
        "sales.SalesInvoice",
        on_delete=models.SET_NULL,
        related_name="customer_receivables",
        null=True,
        blank=True,
        verbose_name=_("Source Sales Invoice"),
        db_index=True,
    )

    receivable_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Receivable Number (AR)"))

    original_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Original Obligation Amount"))
    paid_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Total Amount Paid"))
    credit_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Store Credit / Return Credit Applied"))
    refund_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Refund Amount Applied"))
    adjusted_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Adjusted Amount"))
    outstanding_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Net Outstanding Balance"))

    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal("1.000000"), verbose_name=_("Exchange Rate"))

    invoice_date = models.DateField(default=timezone.now, verbose_name=_("Invoice / Obligation Date"))
    due_date = models.DateField(verbose_name=_("Payment Due Date"), db_index=True)

    status = models.CharField(
        max_length=30,
        choices=ARStatus.choices,
        default=ARStatus.OPEN,
        db_index=True,
        verbose_name=_("AR Status"),
    )

    idempotency_key = models.CharField(max_length=100, blank=True, default="", db_index=True, verbose_name=_("Idempotency Key"))
    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        db_table = "customer_receivables"
        verbose_name = _("Customer Receivable")
        verbose_name_plural = _("Customer Receivables")
        ordering = ["due_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "receivable_number"],
                name="ar_receivable_tenant_number_uniq",
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "customer"]),
            models.Index(fields=["tenant", "due_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.receivable_number} - {self.customer.english_name} [${self.outstanding_amount}]"

    def recalculate_balances(self) -> None:
        """Recalculate outstanding amount and update status."""
        self.outstanding_amount = self.original_amount - self.paid_amount - self.credit_amount - self.adjusted_amount + self.refund_amount
        if self.outstanding_amount <= Decimal("0.0000"):
            self.outstanding_amount = Decimal("0.0000")
            if self.status not in [ARStatus.CANCELLED, ARStatus.WRITTEN_OFF, ARStatus.REVERSED]:
                self.status = ARStatus.PAID
        elif self.paid_amount > Decimal("0.0000") or self.credit_amount > Decimal("0.0000") or self.adjusted_amount > Decimal("0.0000"):
            if self.status not in [ARStatus.DISPUTED, ARStatus.CANCELLED, ARStatus.WRITTEN_OFF, ARStatus.REVERSED]:
                self.status = ARStatus.PARTIALLY_PAID
        else:
            if self.due_date < timezone.now().date() and self.status not in [ARStatus.DISPUTED, ARStatus.CANCELLED, ARStatus.WRITTEN_OFF, ARStatus.REVERSED]:
                self.status = ARStatus.OVERDUE
            elif self.status not in [ARStatus.DISPUTED, ARStatus.CANCELLED, ARStatus.WRITTEN_OFF, ARStatus.REVERSED]:
                self.status = ARStatus.OPEN
