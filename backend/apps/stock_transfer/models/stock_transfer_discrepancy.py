"""StockTransferDiscrepancy entity model."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.stock_transfer.models.enums import DiscrepancyStatus, DiscrepancyType


class StockTransferDiscrepancy(TenantAwareModel, FullAuditModel):
    """Record of physical quantity, batch, damage, or item discrepancies reported during transfer receiving."""

    discrepancy_number = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name=_("Discrepancy Number"),
    )
    stock_transfer = models.ForeignKey(
        "stock_transfer.StockTransfer",
        on_delete=models.CASCADE,
        related_name="discrepancies",
        verbose_name=_("Stock Transfer Document"),
        db_index=True,
    )
    transfer_line = models.ForeignKey(
        "stock_transfer.StockTransferLine",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="discrepancies",
        verbose_name=_("Stock Transfer Line"),
    )
    discrepancy_type = models.CharField(
        max_length=50,
        choices=DiscrepancyType.choices,
        default=DiscrepancyType.SHORTAGE,
        db_index=True,
        verbose_name=_("Discrepancy Type"),
    )

    expected_quantity = models.DecimalField(
        max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Expected Quantity")
    )
    actual_quantity = models.DecimalField(
        max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Actual Quantity")
    )
    difference_quantity = models.DecimalField(
        max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Difference Quantity")
    )

    expected_batch = models.ForeignKey(
        "inventory.Batch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expected_discrepancies",
        verbose_name=_("Expected Batch"),
    )
    received_batch = models.ForeignKey(
        "inventory.Batch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_discrepancies",
        verbose_name=_("Received Batch"),
    )
    expected_medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expected_discrepancies",
        verbose_name=_("Expected Medicine"),
    )
    received_medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_discrepancies",
        verbose_name=_("Received Medicine"),
    )

    reason = models.TextField(verbose_name=_("Discrepancy Reason"))
    evidence = models.TextField(blank=True, verbose_name=_("Evidence / Observations"))
    status = models.CharField(
        max_length=50,
        choices=DiscrepancyStatus.choices,
        default=DiscrepancyStatus.REPORTED,
        db_index=True,
        verbose_name=_("Discrepancy Status"),
    )

    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reported_discrepancies",
        verbose_name=_("Reported By"),
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_discrepancies",
        verbose_name=_("Reviewed By"),
    )
    resolution = models.TextField(blank=True, verbose_name=_("Resolution Notes"))
    resolution_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Resolution Date"))

    class Meta:
        db_table = "stock_transfer_discrepancy"
        verbose_name = _("Stock Transfer Discrepancy")
        verbose_name_plural = _("Stock Transfer Discrepancies")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "discrepancy_number"],
                name="stock_transfer_discrepancy_tenant_number_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "stock_transfer"]),
            models.Index(fields=["tenant", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.discrepancy_number} - {self.get_discrepancy_type_display()} ({self.get_status_display()})"
