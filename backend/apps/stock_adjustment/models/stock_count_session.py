"""StockCountSession model for assignment management."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.stock_adjustment.models.enums import SessionStatus
from apps.stock_adjustment.models.stock_count import StockCount
from apps.users.models import User
from apps.warehouses.models import StorageLocation, Warehouse


class StockCountSession(TenantAwareModel, FullAuditModel):
    """Session management for assigning counting responsibilities to users/devices."""

    stock_count = models.ForeignKey(
        StockCount,
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name=_("Stock Count Document"),
        db_index=True,
    )
    session_number = models.CharField(max_length=100, db_index=True, verbose_name=_("Session Number"))
    assigned_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="count_sessions",
        verbose_name=_("Assigned Counter User"),
        db_index=True,
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="count_sessions",
        verbose_name=_("Warehouse"),
    )
    storage_location = models.ForeignKey(
        StorageLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="count_sessions",
        verbose_name=_("Storage Location"),
    )
    session_status = models.CharField(
        max_length=50,
        choices=SessionStatus.choices,
        default=SessionStatus.ACTIVE,
        verbose_name=_("Session Status"),
    )
    started_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Started At"))
    ended_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Ended At"))
    device_info = models.CharField(max_length=255, blank=True, verbose_name=_("Device Context Info"))

    class Meta:
        db_table = "stock_count_session"
        verbose_name = _("Stock Count Session")
        verbose_name_plural = _("Stock Count Sessions")
        ordering = ["-created_at"]
