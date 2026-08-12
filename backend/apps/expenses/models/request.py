"""ExpenseRequest pre-approval workflow model."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.expenses.models.enums import RequestStatus


class ExpenseRequest(TenantAwareModel, FullAuditModel):
    """Pre-approval request workflow for upcoming operational expenses."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="expense_requests",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="expense_requests",
        null=True,
        blank=True,
        verbose_name=_("Branch Scope"),
    )
    category = models.ForeignKey(
        "expenses.ExpenseCategory",
        on_delete=models.PROTECT,
        related_name="requests",
        verbose_name=_("Expense Category"),
    )

    request_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Request Number (EXR)"))
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="submitted_expense_requests",
        verbose_name=_("Requester"),
    )

    department_name = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Department"))
    cost_center_code = models.CharField(max_length=50, blank=True, default="", verbose_name=_("Cost Center Code"))

    estimated_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Estimated Amount"))
    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))

    purpose = models.CharField(max_length=255, verbose_name=_("Expense Purpose"))
    business_justification = models.TextField(blank=True, default="", verbose_name=_("Business Justification"))
    required_date = models.DateField(default=timezone.now, verbose_name=_("Required Date"))

    status = models.CharField(
        max_length=25,
        choices=RequestStatus.choices,
        default=RequestStatus.DRAFT,
        db_index=True,
        verbose_name=_("Request Status"),
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_expense_requests",
        null=True,
        blank=True,
        verbose_name=_("Approved By"),
    )
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="rejected_expense_requests",
        null=True,
        blank=True,
        verbose_name=_("Rejected By"),
    )

    approval_notes = models.TextField(blank=True, default="", verbose_name=_("Approval / Rejection Notes"))

    class Meta:
        db_table = "expense_requests"
        verbose_name = _("Expense Request")
        verbose_name_plural = _("Expense Requests")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "request_number"],
                name="exr_tenant_number_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.request_number} - {self.purpose} (${self.estimated_amount})"
