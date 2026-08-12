"""JournalEntry and JournalEntryLine double-entry accounting models."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.general_ledger.models.enums import JournalStatus


class JournalEntry(TenantAwareModel, FullAuditModel):
    """Header record representing an immutable double-entry accounting journal transaction."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="journal_entries",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="journal_entries",
        null=True,
        blank=True,
        verbose_name=_("Branch Scope"),
    )
    accounting_period = models.ForeignKey(
        "general_ledger.AccountingPeriod",
        on_delete=models.SET_NULL,
        related_name="journal_entries",
        null=True,
        blank=True,
        verbose_name=_("Accounting Period"),
    )

    journal_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Journal Number (JRN)"))
    journal_date = models.DateField(default=timezone.now, db_index=True, verbose_name=_("Journal Date"))
    posting_date = models.DateField(default=timezone.now, db_index=True, verbose_name=_("Posting Date"))

    reference_type = models.CharField(max_length=50, blank=True, default="", db_index=True, verbose_name=_("Reference Type"))
    reference_id = models.CharField(max_length=100, blank=True, default="", db_index=True, verbose_name=_("Reference ID"))
    reference_number = models.CharField(max_length=100, blank=True, default="", db_index=True, verbose_name=_("Reference Number"))
    source_module = models.CharField(max_length=50, blank=True, default="", db_index=True, verbose_name=_("Source Module"))

    description = models.TextField(verbose_name=_("Journal Transaction Description"))
    status = models.CharField(
        max_length=30,
        choices=JournalStatus.choices,
        default=JournalStatus.DRAFT,
        db_index=True,
        verbose_name=_("Journal Status"),
    )

    total_debit = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Total Debit"))
    total_credit = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Total Credit"))
    is_balanced = models.BooleanField(default=False, verbose_name=_("Is Balanced (Debits = Credits)"))

    idempotency_key = models.CharField(max_length=100, blank=True, default="", db_index=True, verbose_name=_("Idempotency Key"))
    posted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Posted At"))
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="posted_journal_entries",
        null=True,
        blank=True,
        verbose_name=_("Posted By"),
    )

    class Meta:
        db_table = "gl_journal_entries"
        verbose_name = _("Journal Entry")
        verbose_name_plural = _("Journal Entries")
        ordering = ["-posting_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "journal_number"],
                name="gl_journal_tenant_number_uniq",
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "posting_date"]),
            models.Index(fields=["tenant", "reference_type", "reference_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.journal_number} - {self.description[:40]} [Debit: ${self.total_debit} / Credit: ${self.total_credit}]"


class JournalEntryLine(TenantAwareModel, FullAuditModel):
    """Line item inside a JournalEntry detailing specific Debit or Credit amount posted to a ChartOfAccount."""

    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name=_("Journal Entry Header"),
        db_index=True,
    )
    account = models.ForeignKey(
        "general_ledger.ChartOfAccount",
        on_delete=models.PROTECT,
        related_name="journal_lines",
        verbose_name=_("Chart of Account"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="gl_journal_lines",
        null=True,
        blank=True,
        verbose_name=_("Branch Scope"),
    )

    description = models.CharField(max_length=255, blank=True, default="", verbose_name=_("Line Description"))

    debit = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Debit Amount"))
    credit = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Credit Amount"))

    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal("1.000000"), verbose_name=_("Exchange Rate"))

    base_debit = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Base Currency Debit Amount"))
    base_credit = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Base Currency Credit Amount"))

    class Meta:
        db_table = "gl_journal_entry_lines"
        verbose_name = _("Journal Entry Line")
        verbose_name_plural = _("Journal Entry Lines")
        ordering = ["created_at"]
