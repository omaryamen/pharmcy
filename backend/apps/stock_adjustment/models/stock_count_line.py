"""StockCountLine model — individual line items for a physical stock count."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.stock_adjustment.models.enums import VarianceDirection


class StockCountLine(TenantAwareModel, FullAuditModel):
    """Line item detailing individual medicine/batch snapshot vs physical count values."""

    stock_count = models.ForeignKey(
        "stock_adjustment.StockCount",
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name=_("Stock Count Document"),
        db_index=True,
    )
    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.CASCADE,
        related_name="stock_count_lines",
        verbose_name=_("Medicine"),
        db_index=True,
    )
    batch = models.ForeignKey(
        "inventory.Batch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_count_lines",
        verbose_name=_("Batch"),
        db_index=True,
    )
    storage_location = models.ForeignKey(
        "warehouses.StorageLocation",
        on_delete=models.CASCADE,
        related_name="stock_count_lines",
        verbose_name=_("Storage Location"),
        db_index=True,
    )

    # Quantities
    snapshot_quantity = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal("0.0000"),
        verbose_name=_("System Snapshot Quantity"),
        help_text=_("System on-hand quantity captured at snapshot time."),
    )
    counted_quantity = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal("0.0000"),
        verbose_name=_("Physically Counted Quantity"),
    )
    variance_quantity = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal("0.0000"),
        verbose_name=_("Variance Quantity"),
        help_text=_("counted_quantity - snapshot_quantity"),
    )
    variance_percentage = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        default=Decimal("0.0000"),
        verbose_name=_("Variance Percentage"),
    )
    variance_cost = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal("0.0000"),
        verbose_name=_("Variance Cost"),
        help_text=_("variance_quantity * unit_cost"),
    )
    unit_cost = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal("0.0000"),
        verbose_name=_("Unit Cost at Snapshot"),
    )
    variance_direction = models.CharField(
        max_length=20,
        choices=VarianceDirection.choices,
        default=VarianceDirection.NO_VARIANCE,
        verbose_name=_("Variance Direction"),
        db_index=True,
    )

    # Recount tracking
    requires_recount = models.BooleanField(default=False, verbose_name=_("Requires Recount"))
    recount_reason = models.CharField(max_length=255, blank=True, verbose_name=_("Recount Reason"))

    # Accountability
    counted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_count_line_counts",
        verbose_name=_("Counted By"),
    )
    notes = models.TextField(blank=True, verbose_name=_("Line Notes"))

    class Meta:
        db_table = "stock_count_line"
        verbose_name = _("Stock Count Line")
        verbose_name_plural = _("Stock Count Lines")
        ordering = ["stock_count", "medicine"]
        indexes = [
            models.Index(fields=["tenant", "stock_count"]),
            models.Index(fields=["tenant", "medicine"]),
            models.Index(fields=["tenant", "variance_direction"]),
        ]

    def __str__(self) -> str:
        return f"{self.stock_count} / {self.medicine} [{self.variance_direction}]"

    def recalculate_variance(self) -> None:
        """Recompute variance fields from snapshot and counted quantities."""
        self.variance_quantity = self.counted_quantity - self.snapshot_quantity
        if self.snapshot_quantity and self.snapshot_quantity != Decimal("0"):
            self.variance_percentage = (self.variance_quantity / self.snapshot_quantity * Decimal("100")).quantize(
                Decimal("0.0001")
            )
        else:
            self.variance_percentage = Decimal("0.0000")
        self.variance_cost = (self.variance_quantity * self.unit_cost).quantize(Decimal("0.0001"))

        if self.variance_quantity > Decimal("0"):
            self.variance_direction = VarianceDirection.OVERAGE
        elif self.variance_quantity < Decimal("0"):
            self.variance_direction = VarianceDirection.SHORTAGE
        else:
            self.variance_direction = VarianceDirection.NO_VARIANCE
