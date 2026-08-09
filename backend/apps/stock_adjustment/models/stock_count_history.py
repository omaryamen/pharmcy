"""StockCountHistory audit log event entity."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.stock_adjustment.models.stock_count import StockCount
from apps.users.models import User


class StockCountHistory(TenantAwareModel, FullAuditModel):
    """Audit log of status lifecycle transitions and variance adjustments for StockCount."""

    stock_count = models.ForeignKey(
        StockCount,
        on_delete=models.CASCADE,
        related_name="history",
        verbose_name=_("Stock Count Document"),
        db_index=True,
    )
    event_type = models.CharField(max_length=100, db_index=True, verbose_name=_("Audit Event Type"))
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_count_history_events",
        verbose_name=_("Performed By User"),
    )
    details = models.JSONField(default=dict, blank=True, verbose_name=_("Audit Event Details"))
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("Event Timestamp"))

    class Meta:
        db_table = "stock_count_history"
        verbose_name = _("Stock Count History")
        verbose_name_plural = _("Stock Count Histories")
        ordering = ["-timestamp"]
