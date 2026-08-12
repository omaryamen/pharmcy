"""ReceivableDispute domain model."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts_receivable.models.enums import DisputeReason, DisputeStatus
from apps.common.models import FullAuditModel, TenantAwareModel


class ReceivableDispute(TenantAwareModel, FullAuditModel):
    """Record of formal customer invoice dispute."""

    receivable = models.ForeignKey(
        "accounts_receivable.CustomerReceivable",
        on_delete=models.CASCADE,
        related_name="disputes",
        verbose_name=_("Receivable"),
        db_index=True,
    )

    dispute_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Dispute Number (DSP)"))
    dispute_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Disputed Amount"))
    reason = models.CharField(
        max_length=40,
        choices=DisputeReason.choices,
        default=DisputeReason.WRONG_AMOUNT,
        verbose_name=_("Dispute Reason"),
    )
    status = models.CharField(
        max_length=30,
        choices=DisputeStatus.choices,
        default=DisputeStatus.OPEN,
        db_index=True,
        verbose_name=_("Dispute Status"),
    )

    description = models.TextField(verbose_name=_("Dispute Description"))
    resolution_notes = models.TextField(blank=True, default="", verbose_name=_("Resolution Notes"))

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="reviewed_ar_disputes",
        null=True,
        blank=True,
        verbose_name=_("Reviewed By"),
    )
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Resolved At"))

    class Meta:
        db_table = "receivable_disputes"
        verbose_name = _("Receivable Dispute")
        verbose_name_plural = _("Receivable Disputes")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "dispute_number"],
                name="ar_dispute_tenant_number_uniq",
            )
        ]
