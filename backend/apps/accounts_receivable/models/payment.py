"""CustomerPayment and CustomerPaymentAllocation subledger domain models."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.accounts_receivable.models.enums import ARPaymentMethod, ARPaymentStatus
from apps.common.models import FullAuditModel, TenantAwareModel


class CustomerPayment(TenantAwareModel, FullAuditModel):
    """Financial record of payment received from a customer."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="customer_ar_payments",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="customer_ar_payments",
        null=True,
        blank=True,
        verbose_name=_("Branch"),
        db_index=True,
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="ar_payments",
        verbose_name=_("Customer"),
        db_index=True,
    )

    payment_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Payment Number (CPY)"))
    payment_date = models.DateField(default=timezone.now, db_index=True, verbose_name=_("Payment Received Date"))
    payment_method = models.CharField(
        max_length=30,
        choices=ARPaymentMethod.choices,
        default=ARPaymentMethod.CASH,
        verbose_name=_("Payment Method"),
    )

    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal("1.000000"), verbose_name=_("Exchange Rate"))

    amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Total Payment Amount"))
    allocated_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Allocated Amount"))
    unallocated_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Unallocated Amount"))

    reference_number = models.CharField(max_length=100, blank=True, default="", verbose_name=_("External Check / Transaction Reference"))
    status = models.CharField(
        max_length=30,
        choices=ARPaymentStatus.choices,
        default=ARPaymentStatus.POSTED,
        db_index=True,
        verbose_name=_("Payment Status"),
    )

    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="posted_customer_ar_payments",
        null=True,
        blank=True,
        verbose_name=_("Posted By"),
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_customer_ar_payments",
        null=True,
        blank=True,
        verbose_name=_("Approved By"),
    )

    reversed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Reversed At"))
    reversed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="reversed_customer_ar_payments",
        null=True,
        blank=True,
        verbose_name=_("Reversed By"),
    )
    reversal_reason = models.TextField(blank=True, default="", verbose_name=_("Reversal Reason"))

    idempotency_key = models.CharField(max_length=100, blank=True, default="", db_index=True, verbose_name=_("Idempotency Key"))
    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        db_table = "customer_ar_payments"
        verbose_name = _("Customer Payment")
        verbose_name_plural = _("Customer Payments")
        ordering = ["-payment_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "payment_number"],
                name="ar_payment_tenant_number_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.payment_number} - {self.customer.english_name} [${self.amount}]"


class CustomerPaymentAllocation(TenantAwareModel, FullAuditModel):
    """Record linking a CustomerPayment to a specific CustomerReceivable obligation."""

    payment = models.ForeignKey(
        CustomerPayment,
        on_delete=models.CASCADE,
        related_name="allocations",
        verbose_name=_("Customer Payment"),
        db_index=True,
    )
    receivable = models.ForeignKey(
        "accounts_receivable.CustomerReceivable",
        on_delete=models.CASCADE,
        related_name="allocations",
        verbose_name=_("Customer Receivable"),
        db_index=True,
    )

    allocated_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Allocated Amount"))
    allocation_date = models.DateField(default=timezone.now, verbose_name=_("Allocation Date"))

    class Meta:
        db_table = "customer_ar_payment_allocations"
        verbose_name = _("Customer Payment Allocation")
        verbose_name_plural = _("Customer Payment Allocations")
        ordering = ["-allocation_date", "-created_at"]
