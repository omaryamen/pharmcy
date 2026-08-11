"""StockCountRecount model — audit log of recount requests and secondary count values."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.stock_adjustment.models.enums import RecountStatus


class StockCountRecount(TenantAwareModel, FullAuditModel):
    """Audit log and record of recount requests and secondary count values."""

    stock_count = models.ForeignKey(
        "stock_adjustment.StockCount",
        on_delete=models.CASCADE,
        related_name="recounts",
        verbose_name=_("Stock Count Document"),
        db_index=True,
    )
    stock_count_line = models.ForeignKey(
        "stock_adjustment.StockCountLine",
        on_delete=models.CASCADE,
        related_name="recount_history",
        verbose_name=_("Stock Count Line"),
        db_index=True,
    )
    recount_number = models.CharField(max_length=100, db_index=True, verbose_name=_("Recount Number"))
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_recounts",
        verbose_name=_("Requested By"),
    )
    recounted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="performed_recounts",
        verbose_name=_("Recounted By"),
    )
    recount_status = models.CharField(
        max_length=30,
        choices=RecountStatus.choices,
        default=RecountStatus.PENDING,
        verbose_name=_("Recount Status"),
        db_index=True,
    )
    original_counted_quantity = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal("0.0000"),
        verbose_name=_("Original Counted Quantity"),
    )
    recount_quantity = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal("0.0000"),
        verbose_name=_("Recount Quantity"),
    )
    reason = models.CharField(max_length=255, blank=True, verbose_name=_("Recount Reason"))
    notes = models.TextField(blank=True, verbose_name=_("Recount Notes"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Recount Completed At"))

    class Meta:
        db_table = "stock_count_recount"
        verbose_name = _("Stock Count Recount")
        verbose_name_plural = _("Stock Count Recounts")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant", "stock_count"]),
            models.Index(fields=["tenant", "recount_status"]),
        ]

    def __str__(self) -> str:
        return f"{self.recount_number} ({self.recount_status})"
