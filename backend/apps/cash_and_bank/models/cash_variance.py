"""CashVariance domain model for cashier till shortages or overages during session closing."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.cash_and_bank.models.enums import VarianceType
from apps.common.models import FullAuditModel, TenantAwareModel


class CashVariance(TenantAwareModel, FullAuditModel):
    """Audit log recorded when actual cash counted at session close does not equal expected cash."""

    register_session = models.ForeignKey(
        "sales.RegisterSession",
        on_delete=models.CASCADE,
        related_name="variances",
        verbose_name=_("POS Register Session"),
        db_index=True,
    )

    variance_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Variance Code (CVR)"))
    variance_type = models.CharField(
        max_length=20,
        choices=VarianceType.choices,
        default=VarianceType.SHORTAGE,
        db_index=True,
        verbose_name=_("Variance Type"),
    )

    expected_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Expected Cash Amount"))
    actual_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Actual Cash Counted"))
    variance_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Variance Amount"))

    reason = models.TextField(blank=True, default="", verbose_name=_("Cashier Reason / Explanation"))
    status = models.CharField(max_length=20, default="pending", db_index=True, verbose_name=_("Resolution Status (pending, approved, written_off)"))

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_cash_variances",
        null=True,
        blank=True,
        verbose_name=_("Approving Manager"),
    )

    class Meta:
        db_table = "cash_variances"
        verbose_name = _("Cash Variance")
        verbose_name_plural = _("Cash Variances")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "variance_number"],
                name="cvr_tenant_number_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.variance_number} [{self.variance_type}] ${self.variance_amount}"
