"""CashDeposit, CashWithdrawal, and CashTransfer treasury operation models."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.cash_and_bank.models.enums import OperationStatus
from apps.common.models import FullAuditModel, TenantAwareModel


class CashDeposit(TenantAwareModel, FullAuditModel):
    """Treasury operation depositing physical cash from a CashAccount into a BankAccount."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="cash_deposits",
        verbose_name=_("Company"),
        db_index=True,
    )
    cash_account = models.ForeignKey(
        "cash_and_bank.CashAccount",
        on_delete=models.PROTECT,
        related_name="deposits",
        verbose_name=_("Source Cash Account"),
    )
    bank_account = models.ForeignKey(
        "cash_and_bank.BankAccount",
        on_delete=models.PROTECT,
        related_name="deposits",
        verbose_name=_("Destination Bank Account"),
    )

    deposit_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Deposit Number (DEP)"))
    deposit_date = models.DateField(default=timezone.now, verbose_name=_("Deposit Date"))

    amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Deposit Amount"))
    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))

    reference = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Reference / Slip Number"))
    status = models.CharField(
        max_length=25,
        choices=OperationStatus.choices,
        default=OperationStatus.POSTED,
        db_index=True,
        verbose_name=_("Operation Status"),
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_cash_deposits",
        null=True,
        blank=True,
        verbose_name=_("Approved By"),
    )
    posted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Posted At"))

    class Meta:
        db_table = "cash_deposits"
        verbose_name = _("Cash Deposit")
        verbose_name_plural = _("Cash Deposits")
        ordering = ["-deposit_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "deposit_number"],
                name="dep_tenant_number_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.deposit_number} (${self.amount}) -> {self.bank_account.bank_name}"


class CashWithdrawal(TenantAwareModel, FullAuditModel):
    """Treasury operation withdrawing funds from a BankAccount into a CashAccount."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="cash_withdrawals",
        verbose_name=_("Company"),
        db_index=True,
    )
    bank_account = models.ForeignKey(
        "cash_and_bank.BankAccount",
        on_delete=models.PROTECT,
        related_name="withdrawals",
        verbose_name=_("Source Bank Account"),
    )
    cash_account = models.ForeignKey(
        "cash_and_bank.CashAccount",
        on_delete=models.PROTECT,
        related_name="withdrawals",
        verbose_name=_("Destination Cash Account"),
    )

    withdrawal_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Withdrawal Number (WTH)"))
    withdrawal_date = models.DateField(default=timezone.now, verbose_name=_("Withdrawal Date"))

    amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Withdrawal Amount"))
    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))

    purpose = models.CharField(max_length=200, blank=True, default="", verbose_name=_("Withdrawal Purpose"))
    reference = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Reference"))
    status = models.CharField(
        max_length=25,
        choices=OperationStatus.choices,
        default=OperationStatus.POSTED,
        db_index=True,
        verbose_name=_("Operation Status"),
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_cash_withdrawals",
        null=True,
        blank=True,
        verbose_name=_("Approved By"),
    )
    posted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Posted At"))

    class Meta:
        db_table = "cash_withdrawals"
        verbose_name = _("Cash Withdrawal")
        verbose_name_plural = _("Cash Withdrawals")
        ordering = ["-withdrawal_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "withdrawal_number"],
                name="wth_tenant_number_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.withdrawal_number} (${self.amount}) -> {self.cash_account.name}"


class CashTransfer(TenantAwareModel, FullAuditModel):
    """Treasury operation transferring physical cash between two CashAccounts (e.g. Vault -> Till)."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="cash_transfers",
        verbose_name=_("Company"),
        db_index=True,
    )
    source_cash_account = models.ForeignKey(
        "cash_and_bank.CashAccount",
        on_delete=models.PROTECT,
        related_name="outgoing_transfers",
        verbose_name=_("Source Cash Account"),
    )
    destination_cash_account = models.ForeignKey(
        "cash_and_bank.CashAccount",
        on_delete=models.PROTECT,
        related_name="incoming_transfers",
        verbose_name=_("Destination Cash Account"),
    )

    transfer_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Transfer Number (CTF)"))
    transfer_date = models.DateField(default=timezone.now, verbose_name=_("Transfer Date"))

    amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Transfer Amount"))
    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))

    reference = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Reference"))
    status = models.CharField(
        max_length=25,
        choices=OperationStatus.choices,
        default=OperationStatus.POSTED,
        db_index=True,
        verbose_name=_("Operation Status"),
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_cash_transfers",
        null=True,
        blank=True,
        verbose_name=_("Approved By"),
    )
    posted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Posted At"))

    class Meta:
        db_table = "cash_transfers"
        verbose_name = _("Cash Transfer")
        verbose_name_plural = _("Cash Transfers")
        ordering = ["-transfer_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "transfer_number"],
                name="ctf_tenant_number_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.transfer_number} (${self.amount}) {self.source_cash_account.name} -> {self.destination_cash_account.name}"
