"""BankTransaction domain model with duplicate import protection."""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.cash_and_bank.models.enums import BankTransactionType, ReconciliationMatchStatus
from apps.common.models import FullAuditModel, TenantAwareModel


class BankTransaction(TenantAwareModel, FullAuditModel):
    """External bank statement transaction line with strict import hash duplicate protection."""

    bank_account = models.ForeignKey(
        "cash_and_bank.BankAccount",
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name=_("Bank Account"),
        db_index=True,
    )

    transaction_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Transaction Number (BTX)"))
    external_id = models.CharField(max_length=100, blank=True, default="", db_index=True, verbose_name=_("Bank External ID"))
    import_hash = models.CharField(max_length=64, db_index=True, verbose_name=_("Unique Import Hash Fingerprint"))

    transaction_date = models.DateField(default=timezone.now, db_index=True, verbose_name=_("Transaction Date"))
    value_date = models.DateField(default=timezone.now, verbose_name=_("Value Date"))

    transaction_type = models.CharField(
        max_length=25,
        choices=BankTransactionType.choices,
        default=BankTransactionType.DEPOSIT,
        db_index=True,
        verbose_name=_("Transaction Type"),
    )

    amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Transaction Amount (+ Deposit, - Withdrawal)"))
    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))

    reference = models.CharField(max_length=150, blank=True, default="", verbose_name=_("Bank Reference"))
    description = models.TextField(blank=True, default="", verbose_name=_("Transaction Description"))

    reconciliation_status = models.CharField(
        max_length=25,
        choices=ReconciliationMatchStatus.choices,
        default=ReconciliationMatchStatus.UNMATCHED,
        db_index=True,
        verbose_name=_("Reconciliation Status"),
    )

    imported_at = models.DateTimeField(default=timezone.now, verbose_name=_("Imported At"))

    class Meta:
        db_table = "bank_transactions"
        verbose_name = _("Bank Transaction")
        verbose_name_plural = _("Bank Transactions")
        ordering = ["-transaction_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "bank_account", "import_hash"],
                name="btx_tenant_account_hash_uniq",
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "reconciliation_status"]),
            models.Index(fields=["tenant", "transaction_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.transaction_number} [{self.transaction_type}] - ${self.amount} ({self.reconciliation_status})"
