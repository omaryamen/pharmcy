"""StockMovementLine entity model."""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel


class StockMovementLine(FullAuditModel, TenantAwareModel):
    """Line item detailing specific medicine batch, quantity, and source/destination storage location for a stock movement."""

    movement = models.ForeignKey(
        "stock_movement.StockMovement",
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name=_("Stock Movement Document"),
        db_index=True,
    )
    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.CASCADE,
        related_name="movement_lines",
        verbose_name=_("Medicine"),
        db_index=True,
    )
    batch = models.ForeignKey(
        "inventory.Batch",
        on_delete=models.SET_NULL,
        related_name="movement_lines",
        null=True,
        blank=True,
        verbose_name=_("Batch"),
        db_index=True,
    )

    source_location = models.ForeignKey(
        "warehouses.StorageLocation",
        on_delete=models.SET_NULL,
        related_name="source_movement_lines",
        null=True,
        blank=True,
        verbose_name=_("Source Location"),
        db_index=True,
    )
    destination_location = models.ForeignKey(
        "warehouses.StorageLocation",
        on_delete=models.SET_NULL,
        related_name="destination_movement_lines",
        null=True,
        blank=True,
        verbose_name=_("Destination Location"),
        db_index=True,
    )

    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name=_("Movement Line Quantity"),
    )
    unit = models.CharField(
        max_length=30,
        default="Pcs",
        blank=True,
        verbose_name=_("Unit of Measure"),
    )
    unit_cost = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal("0.0000"),
        verbose_name=_("Unit Cost"),
    )
    total_cost = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal("0.0000"),
        verbose_name=_("Total Line Cost"),
    )

    reason = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name=_("Line Reason"),
    )
    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Stock Movement Line"
        verbose_name_plural = "Stock Movement Lines"
        indexes = [
            models.Index(fields=["movement", "medicine"]),
            models.Index(fields=["tenant", "batch"]),
        ]

    def save(self, *args, **kwargs):
        if self.quantity and self.unit_cost and (not self.total_cost or self.total_cost == Decimal("0.0000")):
            self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        batch_str = f" Batch: {self.batch.batch_number}" if self.batch else ""
        return f"{self.quantity} x {self.medicine.english_name}{batch_str} ({self.movement.movement_number})"
