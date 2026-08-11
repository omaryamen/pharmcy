"""SupplierPayment model for Accounts Payable."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts_payable.models.enums import PaymentMethod, PaymentStatus
from apps.common.models import FullAuditModel, TenantAwareModel


class SupplierPayment(TenantAwareModel, FullAuditModel):
    """Supplier payment record against vendor bills / accounts payable entries."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="supplier_payments",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="supplier_payments",
        null=True,
        blank=True,
        verbose_name=_("Branch"),
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.PROTECT,
        related_name="supplier_payments",
        verbose_name=_("Supplier"),
        db_index=True,
    )
    supplier_invoice = models.ForeignKey(
        "accounts_payable.SupplierInvoice",
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("Supplier Invoice"),
        db_index=True,
    )
    accounts_payable_entry = models.ForeignKey(
        "accounts_payable.AccountsPayableEntry",
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("Accounts Payable Entry"),
    )

    payment_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Payment Number (PAY)"))
    payment_date = models.DateField(verbose_name=_("Payment Date"))

    amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Payment Amount"))
    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))

    payment_method = models.CharField(
        max_length=30,
        choices=PaymentMethod.choices,
        default=PaymentMethod.BANK_TRANSFER,
        verbose_name=_("Payment Method"),
    )
    reference_number = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Reference / Check / Transaction ID"))

    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.DRAFT,
        db_index=True,
        verbose_name=_("Payment Status"),
    )

    idempotency_key = models.CharField(max_length=100, blank=True, default="", db_index=True, verbose_name=_("Idempotency Key"))

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_supplier_payments",
        null=True,
        blank=True,
        verbose_name=_("Created By"),
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_supplier_payments",
        null=True,
        blank=True,
        verbose_name=_("Approved By"),
    )

    posted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Posted At"))
    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        db_table = "supplier_payments"
        verbose_name = _("Supplier Payment")
        verbose_name_plural = _("Supplier Payments")
        ordering = ["-payment_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "payment_number"],
                name="supplier_payment_tenant_number_uniq",
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "supplier"]),
        ]

    def __str__(self) -> str:
        return f"{self.payment_number} - {self.supplier.legal_name} ({self.amount} {self.currency})"
