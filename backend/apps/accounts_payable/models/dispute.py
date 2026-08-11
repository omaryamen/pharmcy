"""InvoiceDispute model for tracking vendor bill variances and discrepancies."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts_payable.models.enums import DisputeReason, DisputeStatus
from apps.common.models import FullAuditModel, TenantAwareModel


class InvoiceDispute(TenantAwareModel, FullAuditModel):
    """Dispute record for vendor bills with price or quantity discrepancies."""

    supplier_invoice = models.ForeignKey(
        "accounts_payable.SupplierInvoice",
        on_delete=models.CASCADE,
        related_name="disputes",
        verbose_name=_("Supplier Invoice"),
        db_index=True,
    )

    dispute_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Dispute Number (DISP)"))
    reason = models.CharField(
        max_length=30,
        choices=DisputeReason.choices,
        default=DisputeReason.PRICE_VARIANCE,
        verbose_name=_("Dispute Reason"),
    )

    amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Disputed Amount"))
    evidence = models.TextField(blank=True, default="", verbose_name=_("Evidence / Notes"))

    status = models.CharField(
        max_length=20,
        choices=DisputeStatus.choices,
        default=DisputeStatus.PENDING,
        db_index=True,
        verbose_name=_("Dispute Status"),
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_invoice_disputes",
        null=True,
        blank=True,
        verbose_name=_("Created By"),
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="reviewed_invoice_disputes",
        null=True,
        blank=True,
        verbose_name=_("Reviewed By"),
    )

    resolution = models.TextField(blank=True, default="", verbose_name=_("Resolution Notes"))
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Resolved At"))

    class Meta:
        db_table = "invoice_disputes"
        verbose_name = _("Invoice Dispute")
        verbose_name_plural = _("Invoice Disputes")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.dispute_number} - Invoice {self.supplier_invoice.invoice_number} ({self.reason})"
