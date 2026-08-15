"""CommercePayment and CommerceRefund models settling online orders."""

from __future__ import annotations

from typing import Any
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.commerce.models.enums import CommercePaymentStatus
from apps.commerce.models.order import CommerceOrder


class CommercePayment(TenantAwareModel, FullAuditModel):
    """Payment transaction settling a commerce order."""

    payment_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Payment Number (CPAY)"))

    order = models.ForeignKey(
        CommerceOrder,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("Commerce Order"),
    )

    amount = models.DecimalField(max_digits=12, decimal_places=4, verbose_name=_("Payment Amount"))
    currency = models.CharField(max_length=3, default="USD", verbose_name=_("Currency Code"))

    payment_method = models.CharField(max_length=50, default="card", verbose_name=_("Payment Method (card, cod, wallet, b2b_credit)"))
    status = models.CharField(
        max_length=30,
        choices=CommercePaymentStatus.choices,
        default=CommercePaymentStatus.PENDING,
        db_index=True,
        verbose_name=_("Payment Status"),
    )

    external_tx_id = models.CharField(max_length=150, blank=True, default="", verbose_name=_("External Gateway Transaction ID"))

    class Meta:
        db_table = "commerce_payments"
        verbose_name = _("Commerce Payment")
        verbose_name_plural = _("Commerce Payments")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.payment_number} - {self.amount} {self.currency} for Order {self.order.order_number}"


class CommerceRefund(TenantAwareModel, FullAuditModel):
    """Refund transaction issued against a commerce order payment."""

    refund_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Refund Number (CRFD)"))

    payment = models.ForeignKey(
        CommercePayment,
        on_delete=models.CASCADE,
        related_name="refunds",
        verbose_name=_("Commerce Payment"),
    )

    amount = models.DecimalField(max_digits=12, decimal_places=4, verbose_name=_("Refund Amount"))
    currency = models.CharField(max_length=3, default="USD", verbose_name=_("Currency Code"))
    reason = models.TextField(blank=True, default="", verbose_name=_("Refund Reason"))

    class Meta:
        db_table = "commerce_refunds"
        verbose_name = _("Commerce Refund")
        verbose_name_plural = _("Commerce Refunds")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.refund_number} - {self.amount} {self.currency} on Payment {self.payment.payment_number}"
