"""CashAccount domain model."""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel


class CashAccount(TenantAwareModel, FullAuditModel):
    """Physical or virtual cash account representing a branch till, vault, or petty cash fund."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="cash_accounts",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="cash_accounts",
        null=True,
        blank=True,
        verbose_name=_("Branch Scope"),
    )
    gl_account = models.ForeignKey(
        "general_ledger.ChartOfAccount",
        on_delete=models.SET_NULL,
        related_name="cash_accounts",
        null=True,
        blank=True,
        verbose_name=_("Linked GL Chart of Account"),
    )

    name = models.CharField(max_length=150, verbose_name=_("Cash Account Name"))
    account_number = models.CharField(max_length=50, db_index=True, verbose_name=_("Cash Account Code"))

    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))
    status = models.CharField(max_length=20, default="active", db_index=True, verbose_name=_("Account Status"))

    opening_balance = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Opening Float Balance"))
    current_balance = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Current Cash Balance"))

    description = models.TextField(blank=True, default="", verbose_name=_("Description"))

    class Meta:
        db_table = "cash_accounts"
        verbose_name = _("Cash Account")
        verbose_name_plural = _("Cash Accounts")
        ordering = ["account_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "company", "account_number"],
                name="cash_acc_tenant_company_num_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.account_number} - {self.name} (${self.current_balance})"
