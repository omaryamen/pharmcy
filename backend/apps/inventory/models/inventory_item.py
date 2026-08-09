"""Inventory Item model representing stock balance at a specific storage location and batch."""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.db.models import CheckConstraint, Q
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel
from apps.inventory.models.enums import InventoryStatus
from apps.inventory.validators import validate_inventory_batch, validate_inventory_location, validate_quantity_non_negative


class InventoryItem(FullAuditModel, TenantAwareModel):
    """Stock Position Entity of a Medicine Batch at a Storage Location within a Warehouse."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="inventory_items",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="inventory_items",
        null=True,
        blank=True,
        verbose_name=_("Branch"),
        db_index=True,
    )
    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.CASCADE,
        related_name="inventory_items",
        verbose_name=_("Warehouse"),
        db_index=True,
    )
    storage_location = models.ForeignKey(
        "warehouses.StorageLocation",
        on_delete=models.CASCADE,
        related_name="inventory_items",
        verbose_name=_("Storage Location"),
        db_index=True,
    )
    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.CASCADE,
        related_name="inventory_items",
        verbose_name=_("Medicine"),
        db_index=True,
    )
    batch = models.ForeignKey(
        "inventory.Batch",
        on_delete=models.CASCADE,
        related_name="inventory_items",
        verbose_name=_("Batch"),
        db_index=True,
    )

    status = models.CharField(
        max_length=30,
        choices=InventoryStatus.choices,
        default=InventoryStatus.AVAILABLE,
        db_index=True,
        verbose_name=_("Inventory status"),
    )

    # Quantity Semantics
    on_hand_quantity = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"), verbose_name=_("On hand physical quantity"))
    reserved_quantity = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Reserved quantity"))
    damaged_quantity = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Damaged quantity"))
    quarantine_quantity = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Quarantine quantity"))

    min_quantity = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Minimum stock limit"))
    max_quantity = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Maximum stock capacity"))
    reorder_point = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Reorder threshold point"))

    # Cost & Pricing
    unit_cost = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Unit cost"))
    average_cost = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Weighted average cost"))
    last_cost = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Last purchase unit cost"))
    selling_price = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Current selling price"))

    # Movement and Inventory Audit dates
    last_movement_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Last stock movement date"))
    last_count_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Last physical count date"))

    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        ordering = ["medicine__english_name", "batch__expiry_date"]
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "warehouse", "storage_location", "medicine", "batch"],
                name="inventory_item_wh_loc_med_batch_uniq",
            ),
            CheckConstraint(check=Q(on_hand_quantity__gte=0), name="inventory_on_hand_non_negative"),
            CheckConstraint(check=Q(reserved_quantity__gte=0), name="inventory_reserved_non_negative"),
            CheckConstraint(check=Q(damaged_quantity__gte=0), name="inventory_damaged_non_negative"),
            CheckConstraint(check=Q(quarantine_quantity__gte=0), name="inventory_quarantine_non_negative"),
        ]
        indexes = [
            models.Index(fields=["tenant", "warehouse", "medicine"]),
            models.Index(fields=["tenant", "medicine", "status"]),
            models.Index(fields=["warehouse", "storage_location"]),
            models.Index(fields=["tenant", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.medicine.english_name} @ {self.warehouse.code}/{self.storage_location.code} (On-Hand: {self.on_hand_quantity})"

    @property
    def available_quantity(self) -> Decimal:
        avail = self.on_hand_quantity - self.reserved_quantity - self.damaged_quantity - self.quarantine_quantity
        return max(Decimal("0.00"), avail)

    @property
    def total_cost_value(self) -> Decimal:
        return Decimal(str(self.on_hand_quantity)) * Decimal(str(self.unit_cost))

    def clean(self) -> None:
        super().clean()
        validate_inventory_location(self.storage_location, self.warehouse)
        validate_inventory_batch(self.batch, self.medicine)
        validate_quantity_non_negative(self.on_hand_quantity, "On hand quantity")
        validate_quantity_non_negative(self.reserved_quantity, "Reserved quantity")
        validate_quantity_non_negative(self.damaged_quantity, "Damaged quantity")
        validate_quantity_non_negative(self.quarantine_quantity, "Quarantine quantity")

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
