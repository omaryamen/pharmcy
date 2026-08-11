"""CustomerRefund model for retail return disbursements."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.sales_returns.models.enums import RefundMethod, RefundStatus


class CustomerRefund(TenantAwareModel, FullAuditModel):
    """Refund payment transaction issued to customer for accepted sales return."""

    customer_return = models.ForeignKey(
        "sales_returns.CustomerReturn",
        on_delete=models.CASCADE,
        related_name="refunds",
        verbose_name=_("Customer Return"),
        db_index=True,
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.SET_NULL,
        related_name="customer_refunds",
        null=True,
        blank=True,
        verbose_name=_("Customer"),
        db_index=True,
    )
    sales_invoice = models.ForeignKey(
        "sales.SalesInvoice",
        on_delete=models.PROTECT,
        related_name="refunds",
        verbose_name=_("Original Sales Invoice"),
    )

    refund_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Refund Number (REF)"))
    refund_method = models.CharField(
        max_length=30,
        choices=RefundMethod.choices,
        default=RefundMethod.CASH,
        verbose_name=_("Refund Method"),
    )

    amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Refund Amount"))
    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))
    reference_number = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Refund Reference / Gateway ID"))

    status = models.CharField(
        max_length=20,
        choices=RefundStatus.choices,
        default=RefundStatus.COMPLETED,
        db_index=True,
        verbose_name=_("Refund Status"),
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_customer_refunds",
        null=True,
        blank=True,
        verbose_name=_("Created By"),
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_customer_refunds",
        null=True,
        blank=True,
        verbose_name=_("Approved By"),
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="processed_customer_refunds",
        null=True,
        blank=True,
        verbose_name=_("Processed By"),
    )

    processed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Processed At"))
    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        db_table = "customer_refunds"
        verbose_name = _("Customer Refund")
        verbose_name_plural = _("Customer Refunds")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "refund_number"],
                name="customer_refund_tenant_number_uniq",
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "refund_method"]),
        ]

    def __str__(self) -> str:
        return f"{self.refund_number} - {self.refund_method} ({self.amount} {self.currency})"
