"""StockCountHistory model — immutable audit trail for StockCount lifecycle events."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel


class StockCountHistory(TenantAwareModel, FullAuditModel):
    """Audit log of status lifecycle transitions and variance adjustments for StockCount."""

    stock_count = models.ForeignKey(
        "stock_adjustment.StockCount",
        on_delete=models.CASCADE,
        related_name="history",
        verbose_name=_("Stock Count Document"),
        db_index=True,
    )
    event_type = models.CharField(max_length=100, db_index=True, verbose_name=_("Audit Event Type"))
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_count_history_events",
        verbose_name=_("Performed By User"),
    )
    details = models.JSONField(default=dict, blank=True, verbose_name=_("Event Details"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Event Timestamp"), db_index=True)

    class Meta:
        db_table = "stock_count_history"
        verbose_name = _("Stock Count History Event")
        verbose_name_plural = _("Stock Count History Events")
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["tenant", "stock_count"]),
            models.Index(fields=["tenant", "event_type"]),
            models.Index(fields=["tenant", "timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.stock_count} | {self.event_type} @ {self.timestamp}"
