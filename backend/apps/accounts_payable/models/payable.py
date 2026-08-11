"""AccountsPayableEntry subledger model."""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts_payable.models.enums import APStatus
from apps.common.models import FullAuditModel, TenantAwareModel


class AccountsPayableEntry(TenantAwareModel, FullAuditModel):
    """Subledger record for individual outstanding vendor liability / payable."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="accounts_payable_entries",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="accounts_payable_entries",
        null=True,
        blank=True,
        verbose_name=_("Branch"),
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.PROTECT,
        related_name="accounts_payable_entries",
        verbose_name=_("Supplier"),
        db_index=True,
    )
    supplier_invoice = models.OneToOneField(
        "accounts_payable.SupplierInvoice",
        on_delete=models.CASCADE,
        related_name="accounts_payable_entry",
        verbose_name=_("Supplier Invoice"),
        db_index=True,
    )

    payable_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Payable Number (AP)"))

    original_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Original Payable Amount"))
    paid_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Paid Amount"))
    applied_credit_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Applied Credit Amount"))
    outstanding_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Outstanding Balance"))

    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal("1.000000"), verbose_name=_("Exchange Rate"))

    due_date = models.DateField(verbose_name=_("Due Date"), db_index=True)
    status = models.CharField(
        max_length=20,
        choices=APStatus.choices,
        default=APStatus.OPEN,
        db_index=True,
        verbose_name=_("AP Status"),
    )

    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        db_table = "accounts_payable_entries"
        verbose_name = _("Accounts Payable Entry")
        verbose_name_plural = _("Accounts Payable Entries")
        ordering = ["due_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "payable_number"],
                name="ap_entry_tenant_number_uniq",
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "supplier"]),
            models.Index(fields=["tenant", "due_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.payable_number} - {self.supplier.legal_name} (Outstanding: {self.outstanding_amount} {self.currency})"
