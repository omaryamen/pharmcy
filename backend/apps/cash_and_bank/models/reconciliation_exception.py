"""ReconciliationException domain model for tracking unreconciled financial discrepancies."""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.cash_and_bank.models.enums import ExceptionStatus, ExceptionType
from apps.common.models import FullAuditModel, TenantAwareModel


class ReconciliationException(TenantAwareModel, FullAuditModel):
    """Exception log entry tracking unmatched or mismatched bank/book items requiring review."""

    reconciliation = models.ForeignKey(
        "cash_and_bank.BankReconciliation",
        on_delete=models.CASCADE,
        related_name="exceptions",
        verbose_name=_("Reconciliation Session"),
        null=True,
        blank=True,
    )
    bank_transaction = models.ForeignKey(
        "cash_and_bank.BankTransaction",
        on_delete=models.SET_NULL,
        related_name="exceptions",
        null=True,
        blank=True,
        verbose_name=_("Bank Transaction"),
    )

    exception_type = models.CharField(
        max_length=35,
        choices=ExceptionType.choices,
        default=ExceptionType.MISSING_BOOK_ENTRY,
        db_index=True,
        verbose_name=_("Exception Type"),
    )

    amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Discrepancy Amount"))
    description = models.TextField(verbose_name=_("Exception Details"))

    status = models.CharField(
        max_length=20,
        choices=ExceptionStatus.choices,
        default=ExceptionStatus.OPEN,
        db_index=True,
        verbose_name=_("Resolution Status"),
    )

    resolution_notes = models.TextField(blank=True, default="", verbose_name=_("Resolution Notes"))

    class Meta:
        db_table = "reconciliation_exceptions"
        verbose_name = _("Reconciliation Exception")
        verbose_name_plural = _("Reconciliation Exceptions")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.exception_type} (${self.amount}) [{self.status}]"
