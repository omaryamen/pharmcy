"""Supplier credit note foundation model."""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.purchase_returns.models.enums import CreditNoteStatus


class SupplierCreditNote(TenantAwareModel, FullAuditModel):
    """Financial credit note foundation for supplier purchase returns."""

    purchase_return = models.ForeignKey(
        "purchase_returns.PurchaseReturn",
        on_delete=models.CASCADE,
        related_name="credit_notes",
        verbose_name=_("Purchase Return"),
        db_index=True,
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.PROTECT,
        related_name="credit_notes",
        verbose_name=_("Supplier"),
        db_index=True,
    )

    credit_note_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Credit Note Number"))
    supplier_reference = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Supplier Credit Note Ref."))

    accepted_value = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Accepted Value"))
    tax_value = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Tax Value"))
    net_credit_value = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Net Credit Value"))
    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))

    status = models.CharField(
        max_length=20,
        choices=CreditNoteStatus.choices,
        default=CreditNoteStatus.PENDING,
        db_index=True,
        verbose_name=_("Status"),
    )

    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        db_table = "purchase_return_credit_notes"
        verbose_name = _("Supplier Credit Note")
        verbose_name_plural = _("Supplier Credit Notes")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.credit_note_number} - {self.supplier.legal_name} ({self.net_credit_value} {self.currency})"
