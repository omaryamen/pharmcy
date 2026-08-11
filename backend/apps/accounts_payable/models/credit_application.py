"""CreditApplication model for applying supplier credit notes to vendor invoices."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel


class CreditApplication(TenantAwareModel, FullAuditModel):
    """Tracks application of a SupplierCreditNote against a SupplierInvoice / AP Entry."""

    supplier_credit_note = models.ForeignKey(
        "purchase_returns.SupplierCreditNote",
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name=_("Supplier Credit Note"),
        db_index=True,
    )
    supplier_invoice = models.ForeignKey(
        "accounts_payable.SupplierInvoice",
        on_delete=models.CASCADE,
        related_name="credit_applications",
        verbose_name=_("Supplier Invoice"),
        db_index=True,
    )
    accounts_payable_entry = models.ForeignKey(
        "accounts_payable.AccountsPayableEntry",
        on_delete=models.CASCADE,
        related_name="credit_applications",
        verbose_name=_("Accounts Payable Entry"),
    )

    applied_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Applied Amount"))
    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))

    applied_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Applied At"))
    applied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="applied_supplier_credits",
        null=True,
        blank=True,
        verbose_name=_("Applied By"),
    )

    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        db_table = "supplier_credit_applications"
        verbose_name = _("Credit Application")
        verbose_name_plural = _("Credit Applications")
        ordering = ["-applied_at"]

    def __str__(self) -> str:
        return f"Credit {self.supplier_credit_note.credit_note_number} -> Invoice {self.supplier_invoice.invoice_number} ({self.applied_amount})"
