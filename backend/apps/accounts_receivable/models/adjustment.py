"""ReceivableAdjustment domain model."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts_receivable.models.enums import ARAdjustmentStatus, ARAdjustmentType
from apps.common.models import FullAuditModel, TenantAwareModel


class ReceivableAdjustment(TenantAwareModel, FullAuditModel):
    """Record of debit or credit adjustments applied against a customer receivable."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="ar_adjustments",
        verbose_name=_("Company"),
        db_index=True,
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="ar_adjustments",
        verbose_name=_("Customer"),
        db_index=True,
    )
    receivable = models.ForeignKey(
        "accounts_receivable.CustomerReceivable",
        on_delete=models.CASCADE,
        related_name="adjustments",
        verbose_name=_("Receivable"),
        db_index=True,
    )

    adjustment_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Adjustment Number (ADJ)"))
    adjustment_type = models.CharField(
        max_length=30,
        choices=ARAdjustmentType.choices,
        default=ARAdjustmentType.CREDIT_ADJUSTMENT,
        verbose_name=_("Adjustment Type"),
    )

    amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Adjustment Amount"))
    reason = models.TextField(verbose_name=_("Adjustment Reason"))
    reference = models.CharField(max_length=100, blank=True, default="", verbose_name=_("External Reference"))

    status = models.CharField(
        max_length=30,
        choices=ARAdjustmentStatus.choices,
        default=ARAdjustmentStatus.APPROVED,
        db_index=True,
        verbose_name=_("Adjustment Status"),
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_ar_adjustments",
        null=True,
        blank=True,
        verbose_name=_("Approved By Manager"),
    )

    class Meta:
        db_table = "receivable_adjustments"
        verbose_name = _("Receivable Adjustment")
        verbose_name_plural = _("Receivable Adjustments")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "adjustment_number"],
                name="ar_adjustment_tenant_number_uniq",
            )
        ]
