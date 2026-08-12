"""ExpenseCategory domain model supporting parent-child hierarchy and GL linkage."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel


class ExpenseCategory(TenantAwareModel, FullAuditModel):
    """Hierarchical category classifying operational expenses and linking to General Ledger accounts."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="expense_categories",
        verbose_name=_("Company"),
        db_index=True,
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="children",
        null=True,
        blank=True,
        verbose_name=_("Parent Category"),
    )
    gl_expense_account = models.ForeignKey(
        "general_ledger.ChartOfAccount",
        on_delete=models.SET_NULL,
        related_name="expense_categories",
        null=True,
        blank=True,
        verbose_name=_("Default GL Expense Account"),
    )
    tax_account = models.ForeignKey(
        "general_ledger.ChartOfAccount",
        on_delete=models.SET_NULL,
        related_name="tax_expense_categories",
        null=True,
        blank=True,
        verbose_name=_("Linked Input Tax Account"),
    )

    code = models.CharField(max_length=50, db_index=True, verbose_name=_("Category Code (EXC)"))
    name = models.CharField(max_length=150, verbose_name=_("Category Name"))
    name_ar = models.CharField(max_length=150, blank=True, default="", verbose_name=_("Arabic Name"))
    name_en = models.CharField(max_length=150, blank=True, default="", verbose_name=_("English Name"))

    status = models.CharField(max_length=20, default="active", db_index=True, verbose_name=_("Status (active, inactive)"))
    description = models.TextField(blank=True, default="", verbose_name=_("Description"))

    class Meta:
        db_table = "expense_categories"
        verbose_name = _("Expense Category")
        verbose_name_plural = _("Expense Categories")
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "company", "code"],
                name="exp_cat_tenant_company_code_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"
