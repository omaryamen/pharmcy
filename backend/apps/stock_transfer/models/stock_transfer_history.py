"""StockTransferHistory event audit trail model."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import TenantAwareModel


class StockTransferHistory(TenantAwareModel):
    """Audit log tracking state transitions and events for a StockTransfer document."""

    stock_transfer = models.ForeignKey(
        "stock_transfer.StockTransfer",
        on_delete=models.CASCADE,
        related_name="history",
        verbose_name=_("Stock Transfer Document"),
        db_index=True,
    )
    event_type = models.CharField(max_length=100, db_index=True, verbose_name=_("Event Type"))
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Performed By"),
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("Timestamp"))
    details = models.JSONField(default=dict, blank=True, verbose_name=_("Event Details"))

    class Meta:
        db_table = "stock_transfer_history"
        verbose_name = _("Stock Transfer History")
        verbose_name_plural = _("Stock Transfer History Log")
        ordering = ["timestamp"]
        indexes = [
            models.Index(fields=["tenant", "stock_transfer"]),
            models.Index(fields=["tenant", "event_type"]),
            models.Index(fields=["tenant", "timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.stock_transfer} - {self.event_type} at {self.timestamp}"
