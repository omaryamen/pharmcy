"""StockCountLine detail entity model."""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.inventory.models import Batch
from apps.medicines.models import Medicine
from apps.stock_adjustment.models.enums import VarianceDirection
from apps.stock_adjustment.models.stock_count import StockCount
from apps.warehouses.models import StorageLocation


class StockCountLine(TenantAwareModel, FullAuditModel):
    """Line item detailing individual medicine/batch snapshot vs physical count values."""

    stock_count = models.ForeignKey(
        StockCount,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name=_("Stock Count Document"),
        db_index=True,
    )
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.CASCADE,
        related_name="stock_count_lines",
        verbose_name=_("Medicine"),
        db_index=True,
    )
    batch = models.ForeignKey(
        Batch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_count_lines",
        verbose_name=_("Batch"),
        db_index=True,
    )
    storage_location = models.ForeignKey(
        StorageLocation,
        on_delete=models.CASCADE,
        related_name="stock_count_lines",
        verbose_name=_("Storage Location"),
        db_index=True,
    )
    unit = models.CharField(max_length=50, default="Pcs", verbose_name=_("Unit of Measure"))
    unit_cost = models.DecimalField(
        max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Unit Cost")
    )

    snapshot_quantity = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Snapshot System Quantity")
    )
    counted_quantity = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name=_("Counted Physical Quantity")
    )
    variance_quantity = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Variance Quantity")
    )
    variance_percentage = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Variance Percentage")
    )
    variance_cost = models.DecimalField(
        max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Variance Cost Value")
    )
    variance_direction = models.CharField(
        max_length=30,
        choices=VarianceDirection.choices,
        default=VarianceDirection.NO_VARIANCE,
        db_index=True,
        verbose_name=_("Variance Direction"),
    )

    count_status = models.CharField(max_length=50, default="PENDING", verbose_name=_("Line Count Status"))
    counted_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="counted_lines",
        verbose_name=_("Counted By"),
    )
    counted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Counted At"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"))

    recount_quantity = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name=_("Recounted Quantity")
    )
    recount_requested = models.BooleanField(default=False, verbose_name=_("Recount Requested"))

    class Meta:
        db_table = "stock_count_line"
        verbose_name = _("Stock Count Line")
        verbose_name_plural = _("Stock Count Lines")
        ordering = ["id"]
        indexes = [
            models.Index(fields=["stock_count", "medicine"]),
            models.Index(fields=["tenant", "batch"]),
        ]

    def recalculate_variance(self) -> None:
        """Calculate variance quantity, percentage, value, and direction cleanly."""
        if self.counted_quantity is None:
            self.variance_quantity = Decimal("0.00")
            self.variance_percentage = Decimal("0.00")
            self.variance_cost = Decimal("0.0000")
            self.variance_direction = VarianceDirection.NO_VARIANCE
            return

        snapshot = Decimal(str(self.snapshot_quantity))
        counted = Decimal(str(self.counted_quantity))
        var_qty = counted - snapshot

        self.variance_quantity = var_qty
        self.variance_cost = var_qty * Decimal(str(self.unit_cost))

        if snapshot > Decimal("0.00"):
            self.variance_percentage = ((var_qty / snapshot) * Decimal("100.00")).quantize(Decimal("0.01"))
        else:
            self.variance_percentage = Decimal("100.00") if counted > Decimal("0.00") else Decimal("0.00")

        if var_qty > Decimal("0.00"):
            self.variance_direction = VarianceDirection.OVERAGE
        elif var_qty < Decimal("0.00"):
            self.variance_direction = VarianceDirection.SHORTAGE
        else:
            self.variance_direction = VarianceDirection.NO_VARIANCE

    def save(self, *args, **kwargs) -> None:
        self.recalculate_variance()
        super().save(*args, **kwargs)
