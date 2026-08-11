"""SalesPayment model for retail POS customer sales."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.sales.models.enums import SalesPaymentMethod, SalesPaymentStatus


class SalesPayment(TenantAwareModel, FullAuditModel):
    """Payment record against a SalesInvoice (supports cash, card, wallet, customer credit, and split payments)."""

    sales_invoice = models.ForeignKey(
        "sales.SalesInvoice",
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("Sales Invoice"),
        db_index=True,
    )

    payment_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Payment Number (PAY)"))
    payment_method = models.CharField(
        max_length=30,
        choices=SalesPaymentMethod.choices,
        default=SalesPaymentMethod.CASH,
        verbose_name=_("Payment Method"),
    )

    amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Payment Amount"))
    tendered_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Cash Tendered Amount"))
    change_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Change Returned Amount"))

    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))
    reference_number = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Transaction / Card Reference"))

    status = models.CharField(
        max_length=20,
        choices=SalesPaymentStatus.choices,
        default=SalesPaymentStatus.POSTED,
        db_index=True,
        verbose_name=_("Status"),
    )

    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="cashier_sales_payments",
        null=True,
        blank=True,
        verbose_name=_("Created By"),
    )

    class Meta:
        db_table = "sales_payments"
        verbose_name = _("Sales Payment")
        verbose_name_plural = _("Sales Payments")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "payment_number"],
                name="sales_payment_tenant_number_uniq",
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "payment_method"]),
        ]

    def __str__(self) -> str:
        return f"{self.payment_number} - {self.payment_method} ({self.amount} {self.currency})"
