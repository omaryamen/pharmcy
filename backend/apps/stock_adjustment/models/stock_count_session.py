"""StockCountSession model for assignment management."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.stock_adjustment.models.enums import SessionStatus


class StockCountSession(TenantAwareModel, FullAuditModel):
    """Session management for assigning counting responsibilities to users/devices."""

    stock_count = models.ForeignKey(
        "stock_adjustment.StockCount",
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name=_("Stock Count Document"),
        db_index=True,
    )
    session_number = models.CharField(max_length=100, db_index=True, verbose_name=_("Session Number"))
    assigned_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="count_sessions",
        verbose_name=_("Assigned Counter User"),
        db_index=True,
    )
    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.CASCADE,
        related_name="count_sessions",
        verbose_name=_("Warehouse"),
    )
    storage_location = models.ForeignKey(
        "warehouses.StorageLocation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="count_sessions",
        verbose_name=_("Storage Location"),
    )
    session_status = models.CharField(
        max_length=30,
        choices=SessionStatus.choices,
        default=SessionStatus.PENDING,
        verbose_name=_("Session Status"),
        db_index=True,
    )
    started_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Session Started At"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Session Completed At"))
    notes = models.TextField(blank=True, verbose_name=_("Session Notes"))

    class Meta:
        db_table = "stock_count_session"
        verbose_name = _("Stock Count Session")
        verbose_name_plural = _("Stock Count Sessions")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant", "stock_count"]),
            models.Index(fields=["tenant", "session_status"]),
        ]

    def __str__(self) -> str:
        return f"{self.session_number} ({self.session_status})"
