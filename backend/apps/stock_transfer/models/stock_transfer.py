"""StockTransfer master entity model."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.stock_transfer.models.enums import TransferPriority, TransferStatus, TransferType


class StockTransfer(TenantAwareModel, FullAuditModel):
    """Header record for physical stock movement requests & orders between storage locations, warehouses, or branches."""

    transfer_number = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name=_("Transfer Number"),
    )
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="stock_transfers",
        verbose_name=_("Company"),
        db_index=True,
    )
    source_branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_transfers",
        verbose_name=_("Source Branch"),
        db_index=True,
    )
    destination_branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="destination_transfers",
        verbose_name=_("Destination Branch"),
        db_index=True,
    )
    source_warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.CASCADE,
        related_name="source_transfers",
        verbose_name=_("Source Warehouse"),
        db_index=True,
    )
    destination_warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.CASCADE,
        related_name="destination_transfers",
        verbose_name=_("Destination Warehouse"),
        db_index=True,
    )
    source_location = models.ForeignKey(
        "warehouses.StorageLocation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_location_transfers",
        verbose_name=_("Source Storage Location"),
        db_index=True,
    )
    destination_location = models.ForeignKey(
        "warehouses.StorageLocation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="destination_location_transfers",
        verbose_name=_("Destination Storage Location"),
        db_index=True,
    )
    transfer_type = models.CharField(
        max_length=50,
        choices=TransferType.choices,
        default=TransferType.WAREHOUSE_TRANSFER,
        db_index=True,
        verbose_name=_("Transfer Type"),
    )
    priority = models.CharField(
        max_length=20,
        choices=TransferPriority.choices,
        default=TransferPriority.MEDIUM,
        db_index=True,
        verbose_name=_("Priority"),
    )
    status = models.CharField(
        max_length=50,
        choices=TransferStatus.choices,
        default=TransferStatus.DRAFT,
        db_index=True,
        verbose_name=_("Transfer Status"),
    )

    # User Accountability
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_stock_transfers",
        verbose_name=_("Requested By"),
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_stock_transfers",
        verbose_name=_("Approved By"),
    )
    dispatched_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dispatched_stock_transfers",
        verbose_name=_("Dispatched By"),
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_stock_transfers",
        verbose_name=_("Received By"),
    )
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cancelled_stock_transfers",
        verbose_name=_("Cancelled By"),
    )

    # Timestamps
    requested_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Requested Timestamp"))
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Approved Timestamp"))
    dispatched_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Dispatched Timestamp"))
    received_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Received Timestamp"))
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Cancelled Timestamp"))

    expected_arrival_date = models.DateField(null=True, blank=True, verbose_name=_("Expected Arrival Date"))
    actual_arrival_date = models.DateField(null=True, blank=True, verbose_name=_("Actual Arrival Date"))

    reason = models.CharField(max_length=255, blank=True, verbose_name=_("Reason"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    reference_type = models.CharField(max_length=50, blank=True, verbose_name=_("Reference Type"))
    reference_id = models.CharField(max_length=100, blank=True, verbose_name=_("Reference ID"))

    # Summary Aggregates
    total_items = models.IntegerField(default=0, verbose_name=_("Total Items Count"))
    total_requested_quantity = models.DecimalField(
        max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Total Requested Quantity")
    )
    total_dispatched_quantity = models.DecimalField(
        max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Total Dispatched Quantity")
    )
    total_received_quantity = models.DecimalField(
        max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Total Received Quantity")
    )
    total_cost = models.DecimalField(
        max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Total Transfer Cost")
    )

    idempotency_key = models.CharField(
        max_length=100, blank=True, db_index=True, verbose_name=_("Idempotency Key")
    )
    has_discrepancy = models.BooleanField(
        default=False, db_index=True, verbose_name=_("Has Discrepancy Flag")
    )

    class Meta:
        db_table = "stock_transfer"
        verbose_name = _("Stock Transfer")
        verbose_name_plural = _("Stock Transfers")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "transfer_number"],
                name="stock_transfer_tenant_number_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "transfer_type"]),
            models.Index(fields=["tenant", "source_warehouse"]),
            models.Index(fields=["tenant", "destination_warehouse"]),
            models.Index(fields=["tenant", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.transfer_number} ({self.get_status_display()})"
