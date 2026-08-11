"""StockTransferLine item detail entity model."""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.stock_transfer.models.enums import TransferLineStatus


class StockTransferLine(TenantAwareModel, FullAuditModel):
    """Detail line item for a physical medicine/batch stock transfer order."""

    stock_transfer = models.ForeignKey(
        "stock_transfer.StockTransfer",
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name=_("Stock Transfer Document"),
        db_index=True,
    )
    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.CASCADE,
        related_name="transfer_lines",
        verbose_name=_("Medicine"),
        db_index=True,
    )
    batch = models.ForeignKey(
        "inventory.Batch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transfer_lines",
        verbose_name=_("Batch"),
        db_index=True,
    )
    source_location = models.ForeignKey(
        "warehouses.StorageLocation",
        on_delete=models.CASCADE,
        related_name="source_line_transfers",
        verbose_name=_("Source Storage Location"),
        db_index=True,
    )
    destination_location = models.ForeignKey(
        "warehouses.StorageLocation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="destination_line_transfers",
        verbose_name=_("Destination Storage Location"),
        db_index=True,
    )

    # Quantities
    requested_quantity = models.DecimalField(
        max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Requested Quantity")
    )
    approved_quantity = models.DecimalField(
        max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Approved Quantity")
    )
    picked_quantity = models.DecimalField(
        max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Picked Quantity")
    )
    dispatched_quantity = models.DecimalField(
        max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Dispatched Quantity")
    )
    received_quantity = models.DecimalField(
        max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Received Quantity")
    )
    rejected_quantity = models.DecimalField(
        max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Rejected Quantity")
    )
    damaged_quantity = models.DecimalField(
        max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Damaged Quantity")
    )

    unit = models.CharField(max_length=50, default="Pcs", verbose_name=_("Unit of Measure"))
    unit_cost = models.DecimalField(
        max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Unit Cost")
    )
    total_cost = models.DecimalField(
        max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Total Line Cost")
    )

    status = models.CharField(
        max_length=50,
        choices=TransferLineStatus.choices,
        default=TransferLineStatus.PENDING,
        db_index=True,
        verbose_name=_("Line Status"),
    )
    notes = models.TextField(blank=True, verbose_name=_("Line Notes"))

    class Meta:
        db_table = "stock_transfer_line"
        verbose_name = _("Stock Transfer Line")
        verbose_name_plural = _("Stock Transfer Lines")
        ordering = ["stock_transfer", "medicine"]
        indexes = [
            models.Index(fields=["tenant", "stock_transfer"]),
            models.Index(fields=["tenant", "medicine"]),
            models.Index(fields=["tenant", "batch"]),
        ]

    def __str__(self) -> str:
        return f"{self.stock_transfer} / {self.medicine} ({self.requested_quantity} {self.unit})"

    def recalculate_total_cost(self) -> None:
        """Calculate line total cost based on requested or dispatched quantity and unit cost."""
        qty = self.dispatched_quantity if self.dispatched_quantity > Decimal("0") else self.requested_quantity
        self.total_cost = (qty * self.unit_cost).quantize(Decimal("0.0001"))
