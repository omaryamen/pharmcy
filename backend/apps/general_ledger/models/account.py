"""ChartOfAccount and AccountMapping domain models."""

from __future__ import annotations

from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.general_ledger.models.enums import AccountSubtype, AccountType, MappingPurpose


class ChartOfAccount(TenantAwareModel, FullAuditModel):
    """Authoritative Chart of Accounts model supporting account hierarchy, control accounts, and double-entry postings."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="chart_of_accounts",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="chart_of_accounts",
        null=True,
        blank=True,
        verbose_name=_("Branch Scope"),
    )

    account_code = models.CharField(max_length=50, db_index=True, verbose_name=_("Account Code (e.g. 1100)"))
    account_name = models.CharField(max_length=200, verbose_name=_("Account Name"))
    english_name = models.CharField(max_length=200, blank=True, default="", verbose_name=_("English Name"))
    arabic_name = models.CharField(max_length=200, blank=True, default="", verbose_name=_("Arabic Name"))

    account_type = models.CharField(
        max_length=30,
        choices=AccountType.choices,
        default=AccountType.ASSET,
        db_index=True,
        verbose_name=_("Account Type"),
    )
    account_subtype = models.CharField(
        max_length=40,
        choices=AccountSubtype.choices,
        default=AccountSubtype.CASH,
        verbose_name=_("Account Subtype"),
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="children",
        null=True,
        blank=True,
        verbose_name=_("Parent Account"),
    )

    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))
    status = models.CharField(max_length=20, default="active", db_index=True, verbose_name=_("Account Status"))

    is_system_account = models.BooleanField(default=False, verbose_name=_("Is System Account"))
    is_control_account = models.BooleanField(default=False, verbose_name=_("Is Control Account (Non-postable summary parent)"))
    allow_manual_posting = models.BooleanField(default=True, verbose_name=_("Allow Manual Journal Posting"))

    description = models.TextField(blank=True, default="", verbose_name=_("Description"))

    class Meta:
        db_table = "chart_of_accounts"
        verbose_name = _("Chart of Account")
        verbose_name_plural = _("Chart of Accounts")
        ordering = ["account_code"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "company", "account_code"],
                name="coa_tenant_company_code_uniq",
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "account_type"]),
            models.Index(fields=["tenant", "account_code"]),
        ]

    def __str__(self) -> str:
        return f"{self.account_code} - {self.account_name} ({self.account_type})"


class AccountMapping(TenantAwareModel, FullAuditModel):
    """Configurable integration mapping associating operational transaction purposes to specific ChartOfAccount records."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="account_mappings",
        verbose_name=_("Company"),
        db_index=True,
    )
    purpose = models.CharField(
        max_length=40,
        choices=MappingPurpose.choices,
        db_index=True,
        verbose_name=_("Integration Mapping Purpose"),
    )
    account = models.ForeignKey(
        ChartOfAccount,
        on_delete=models.CASCADE,
        related_name="mappings",
        verbose_name=_("Mapped Chart of Account"),
    )

    class Meta:
        db_table = "gl_account_mappings"
        verbose_name = _("Account Mapping")
        verbose_name_plural = _("Account Mappings")
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "company", "purpose"],
                name="gl_mapping_tenant_company_purpose_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.purpose} -> {self.account.account_code}"
