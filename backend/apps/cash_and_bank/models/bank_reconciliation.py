"""BankReconciliation and ReconciliationMatch domain models."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.cash_and_bank.models.enums import BankReconciliationStatus
from apps.common.models import FullAuditModel, TenantAwareModel


class BankReconciliation(TenantAwareModel, FullAuditModel):
    """Bank statement reconciliation session header."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="bank_reconciliations",
        verbose_name=_("Company"),
        db_index=True,
    )
    bank_account = models.ForeignKey(
        "cash_and_bank.BankAccount",
        on_delete=models.CASCADE,
        related_name="reconciliations",
        verbose_name=_("Bank Account"),
        db_index=True,
    )

    reconciliation_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Reconciliation Code (REC)"))
    start_date = models.DateField(verbose_name=_("Statement Start Date"))
    end_date = models.DateField(verbose_name=_("Statement End Date"))

    opening_balance = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Opening Statement Balance"))
    statement_closing_balance = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Statement Closing Balance"))
    book_closing_balance = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Book Ledger Closing Balance"))
    difference = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Unreconciled Variance"))

    status = models.CharField(
        max_length=25,
        choices=BankReconciliationStatus.choices,
        default=BankReconciliationStatus.DRAFT,
        db_index=True,
        verbose_name=_("Reconciliation Status"),
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_bank_reconciliations",
        null=True,
        blank=True,
        verbose_name=_("Approved By"),
    )
    reconciled_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Reconciled At"))

    class Meta:
        db_table = "bank_reconciliations"
        verbose_name = _("Bank Reconciliation")
        verbose_name_plural = _("Bank Reconciliations")
        ordering = ["-end_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "reconciliation_number"],
                name="brec_tenant_number_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.reconciliation_number} - {self.bank_account.bank_name} [{self.start_date} to {self.end_date}]"


class ReconciliationMatch(TenantAwareModel, FullAuditModel):
    """Link item matching an external BankTransaction to internal book entries."""

    reconciliation = models.ForeignKey(
        BankReconciliation,
        on_delete=models.CASCADE,
        related_name="matches",
        verbose_name=_("Reconciliation Session"),
    )
    bank_transaction = models.ForeignKey(
        "cash_and_bank.BankTransaction",
        on_delete=models.CASCADE,
        related_name="matches",
        verbose_name=_("Bank Transaction"),
    )

    matched_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Matched Amount"))

    reference_type = models.CharField(max_length=50, blank=True, default="", verbose_name=_("Book Entry Type (e.g. CUSTOMER_PAYMENT, DEPOSIT)"))
    reference_id = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Book Entry Reference ID"))

    is_auto_matched = models.BooleanField(default=False, verbose_name=_("Auto-Matched by System"))

    class Meta:
        db_table = "reconciliation_matches"
        verbose_name = _("Reconciliation Match")
        verbose_name_plural = _("Reconciliation Matches")
