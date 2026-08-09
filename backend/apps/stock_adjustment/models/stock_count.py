"""StockCount master entity model."""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.branches.models import Branch
from apps.common.models import FullAuditModel, TenantAwareModel
from apps.companies.models import Company
from apps.stock_adjustment.models.enums import CountScopeType, CountStatus, CountType
from apps.users.models import User
from apps.warehouses.models import StorageLocation, Warehouse


class StockCount(TenantAwareModel, FullAuditModel):
    """Header record for physical stock count inventory auditing sessions."""

    count_number = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name=_("Count Number"),
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="stock_counts",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_counts",
        verbose_name=_("Branch"),
        db_index=True,
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="stock_counts",
        verbose_name=_("Warehouse"),
        db_index=True,
    )
    storage_location = models.ForeignKey(
        StorageLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_counts",
        verbose_name=_("Storage Location"),
        db_index=True,
    )
    count_type = models.CharField(
        max_length=50,
        choices=CountType.choices,
        default=CountType.WAREHOUSE_COUNT,
        db_index=True,
        verbose_name=_("Count Type"),
    )
    count_status = models.CharField(
        max_length=50,
        choices=CountStatus.choices,
        default=CountStatus.DRAFT,
        db_index=True,
        verbose_name=_("Count Status"),
    )
    count_scope_type = models.CharField(
        max_length=50,
        choices=CountScopeType.choices,
        default=CountScopeType.WAREHOUSE,
        verbose_name=_("Count Scope Type"),
    )
    scope_filter = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Scope Filter Parameters"),
        help_text=_("Explicit parameters defining the count scope filter."),
    )
    is_blind_count = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("Is Blind Count"),
        help_text=_("When true, physical counters cannot view system quantities during counting."),
    )
    freeze_inventory = models.BooleanField(
        default=False,
        verbose_name=_("Freeze Inventory"),
        help_text=_("When true, stock movements on the specified scope are locked while count is active."),
    )

    # Timestamps
    snapshot_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Snapshot Timestamp"))
    started_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Started Timestamp"))
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Submitted Timestamp"))
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Reviewed Timestamp"))
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Approved Timestamp"))
    reconciled_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Reconciled Timestamp"))
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Cancelled Timestamp"))

    # User Accountability
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_stock_counts",
        verbose_name=_("Created By"),
    )
    started_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="started_stock_counts",
        verbose_name=_("Started By"),
    )
    completed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="completed_stock_counts",
        verbose_name=_("Completed By"),
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_stock_counts",
        verbose_name=_("Reviewed By"),
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_stock_counts",
        verbose_name=_("Approved By"),
    )
    reconciled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reconciled_stock_counts",
        verbose_name=_("Reconciled By"),
    )

    reason = models.CharField(max_length=255, blank=True, verbose_name=_("Reason"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"))

    # Aggregated Summary Fields
    total_items_counted = models.IntegerField(default=0, verbose_name=_("Total Items Counted"))
    total_shortage_quantity = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Total Shortage Quantity")
    )
    total_overage_quantity = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Total Overage Quantity")
    )
    total_variance_cost = models.DecimalField(
        max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Total Variance Cost")
    )

    idempotency_key = models.CharField(
        max_length=100, blank=True, db_index=True, verbose_name=_("Idempotency Key")
    )

    class Meta:
        db_table = "stock_count"
        verbose_name = _("Stock Count")
        verbose_name_plural = _("Stock Counts")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "count_number"],
                name="stock_count_tenant_number_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "count_status"]),
            models.Index(fields=["tenant", "count_type"]),
            models.Index(fields=["tenant", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.count_number} ({self.get_count_status_display()})"
