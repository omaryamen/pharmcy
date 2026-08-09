"""StockCountRecount history and tracking model."""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.stock_adjustment.models.enums import RecountStatus
from apps.stock_adjustment.models.stock_count import StockCount
from apps.stock_adjustment.models.stock_count_line import StockCountLine
from apps.users.models import User


class StockCountRecount(TenantAwareModel, FullAuditModel):
    """Audit log and record of recount requests and secondary count values."""

    stock_count = models.ForeignKey(
        StockCount,
        on_delete=models.CASCADE,
        related_name="recounts",
        verbose_name=_("Stock Count Document"),
        db_index=True,
    )
    stock_count_line = models.ForeignKey(
        StockCountLine,
        on_delete=models.CASCADE,
        related_name="recount_history",
        verbose_name=_("Stock Count Line"),
        db_index=True,
    )
    recount_number = models.CharField(max_length=100, db_index=True, verbose_name=_("Recount Number"))
    requested_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_recounts",
        verbose_name=_("Requested By"),
    )
    recounted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="performed_recounts",
        verbose_name=_("Recounted By"),
    )
    original_counted_quantity = models.DecimalField(
        max_digits=14, decimal_places=2, verbose_name=_("Original Counted Quantity")
    )
    recounted_quantity = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name=_("Recounted Physical Quantity")
    )
    reason = models.TextField(blank=True, verbose_name=_("Reason for Recount"))
    recount_status = models.CharField(
        max_length=50,
        choices=RecountStatus.choices,
        default=RecountStatus.REQUESTED,
        verbose_name=_("Recount Status"),
    )
    recounted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Recounted At"))

    class Meta:
        db_table = "stock_count_recount"
        verbose_name = _("Stock Count Recount")
        verbose_name_plural = _("Stock Count Recounts")
        ordering = ["-created_at"]
