"""BankAccount domain model."""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel


class BankAccount(TenantAwareModel, FullAuditModel):
    """Institutional bank account model (never stores sensitive credentials)."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="bank_accounts",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="bank_accounts",
        null=True,
        blank=True,
        verbose_name=_("Branch Scope"),
    )
    gl_account = models.ForeignKey(
        "general_ledger.ChartOfAccount",
        on_delete=models.SET_NULL,
        related_name="bank_accounts",
        null=True,
        blank=True,
        verbose_name=_("Linked GL Chart of Account"),
    )

    bank_name = models.CharField(max_length=150, verbose_name=_("Bank Name"))
    account_name = models.CharField(max_length=150, verbose_name=_("Bank Account Title / Holder"))
    account_number = models.CharField(max_length=50, db_index=True, verbose_name=_("Bank Account Number"))
    masked_account_number = models.CharField(max_length=50, blank=True, default="", verbose_name=_("Masked Display Number"))

    iban = models.CharField(max_length=60, blank=True, default="", verbose_name=_("IBAN Number"))
    swift_bic = models.CharField(max_length=30, blank=True, default="", verbose_name=_("SWIFT / BIC Code"))

    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))
    status = models.CharField(max_length=20, default="active", db_index=True, verbose_name=_("Account Status"))

    opening_balance = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Opening Ledger Balance"))
    current_balance = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Current Ledger Balance"))

    description = models.TextField(blank=True, default="", verbose_name=_("Description"))

    class Meta:
        db_table = "bank_accounts"
        verbose_name = _("Bank Account")
        verbose_name_plural = _("Bank Accounts")
        ordering = ["bank_name", "account_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "company", "account_number"],
                name="bank_acc_tenant_company_num_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.bank_name} - {self.account_name} ({self.account_number}) [${self.current_balance}]"
