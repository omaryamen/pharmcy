"""PaymentMethod, SaaSPayment, SaaSPaymentRefund, and PaymentFailureLog models for SaaS billing."""

from __future__ import annotations

from typing import Any
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.saas.models.enums import SaaSPaymentStatus
from apps.saas.models.invoice import SaaSInvoice


class PaymentMethod(TenantAwareModel, FullAuditModel):
    """Tokenized payment method reference stored for recurring tenant billing (PCI compliant - no raw card numbers)."""

    provider_name = models.CharField(max_length=60, default="mock", verbose_name=_("Provider Name"))
    external_token_id = models.CharField(max_length=150, db_index=True, verbose_name=_("External Provider Token ID"))

    brand = models.CharField(max_length=50, blank=True, default="Visa", verbose_name=_("Card Brand"))
    last4 = models.CharField(max_length=4, blank=True, default="4242", verbose_name=_("Last 4 Digits"))
    exp_month = models.IntegerField(default=12, verbose_name=_("Expiry Month"))
    exp_year = models.IntegerField(default=2030, verbose_name=_("Expiry Year"))

    is_default = models.BooleanField(default=True, verbose_name=_("Is Default Payment Method"))

    class Meta:
        db_table = "saas_payment_methods"
        verbose_name = _("Payment Method")
        verbose_name_plural = _("Payment Methods")

    def __str__(self) -> str:
        return f"{self.tenant.name} - {self.brand} ****{self.last4} ({self.provider_name})"


class SaaSPayment(TenantAwareModel, FullAuditModel):
    """Authoritative commercial payment record settling a SaaS invoice."""

    payment_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Payment Number (SPAY)"))

    invoice = models.ForeignKey(
        SaaSInvoice,
        on_delete=models.SET_NULL,
        related_name="payments",
        null=True,
        blank=True,
        verbose_name=_("SaaS Invoice"),
    )

    amount = models.DecimalField(max_digits=12, decimal_places=4, verbose_name=_("Payment Amount"))
    currency = models.CharField(max_length=3, default="USD", verbose_name=_("Currency Code"))

    status = models.CharField(
        max_length=30,
        choices=SaaSPaymentStatus.choices,
        default=SaaSPaymentStatus.PENDING,
        db_index=True,
        verbose_name=_("Payment Status"),
    )

    provider_name = models.CharField(max_length=60, default="mock", verbose_name=_("Provider Name"))
    external_transaction_id = models.CharField(max_length=150, blank=True, default="", verbose_name=_("External Transaction ID"))

    error_code = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Error Code"))
    error_message = models.TextField(blank=True, default="", verbose_name=_("Error Message"))

    class Meta:
        db_table = "saas_payments"
        verbose_name = _("SaaS Payment")
        verbose_name_plural = _("SaaS Payments")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.payment_number} - {self.amount} {self.currency} [{self.status}]"


class SaaSPaymentRefund(TenantAwareModel, FullAuditModel):
    """Refund transaction record against a SaaS payment."""

    refund_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Refund Number (SRFD)"))

    payment = models.ForeignKey(
        SaaSPayment,
        on_delete=models.CASCADE,
        related_name="refunds",
        verbose_name=_("SaaS Payment"),
    )

    amount = models.DecimalField(max_digits=12, decimal_places=4, verbose_name=_("Refund Amount"))
    currency = models.CharField(max_length=3, default="USD", verbose_name=_("Currency Code"))
    reason = models.TextField(blank=True, default="", verbose_name=_("Refund Reason"))

    external_refund_id = models.CharField(max_length=150, blank=True, default="", verbose_name=_("External Provider Refund ID"))

    class Meta:
        db_table = "saas_payment_refunds"
        verbose_name = _("SaaS Payment Refund")
        verbose_name_plural = _("SaaS Payment Refunds")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.refund_number} - {self.amount} {self.currency} for Payment {self.payment.payment_number}"


class PaymentFailureLog(TenantAwareModel, FullAuditModel):
    """Audit log tracking dunning attempts and payment failures for subscriptions."""

    subscription = models.ForeignKey(
        "saas.SaaSSubscription",
        on_delete=models.CASCADE,
        related_name="failure_logs",
        verbose_name=_("SaaS Subscription"),
    )

    attempt_number = models.IntegerField(default=1, verbose_name=_("Attempt Number"))
    error_code = models.CharField(max_length=100, verbose_name=_("Error Code"))
    error_message = models.TextField(verbose_name=_("Error Message"))
    next_retry_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Next Scheduled Retry"))

    class Meta:
        db_table = "saas_payment_failure_logs"
        verbose_name = _("Payment Failure Log")
        verbose_name_plural = _("Payment Failure Logs")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.tenant.name} Attempt #{self.attempt_number} Error: {self.error_code}"
