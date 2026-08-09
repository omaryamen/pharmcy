"""Inventory Transaction model recording all quantity-changing stock movements and audit trails."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel
from apps.inventory.models.enums import AdjustmentReason, TransactionType


class InventoryTransaction(FullAuditModel, TenantAwareModel):
    """Auditable stock transaction log entry for physical stock changes, movements, and reservations."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="inventory_transactions",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="inventory_transactions",
        null=True,
        blank=True,
        verbose_name=_("Branch"),
        db_index=True,
    )
    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.CASCADE,
        related_name="inventory_transactions",
        verbose_name=_("Warehouse"),
        db_index=True,
    )
    storage_location = models.ForeignKey(
        "warehouses.StorageLocation",
        on_delete=models.CASCADE,
        related_name="inventory_transactions",
        verbose_name=_("Storage Location"),
        db_index=True,
    )
    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.CASCADE,
        related_name="inventory_transactions",
        verbose_name=_("Medicine"),
        db_index=True,
    )
    batch = models.ForeignKey(
        "inventory.Batch",
        on_delete=models.CASCADE,
        related_name="inventory_transactions",
        null=True,
        blank=True,
        verbose_name=_("Batch"),
        db_index=True,
    )
    inventory_item = models.ForeignKey(
        "inventory.InventoryItem",
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name=_("Inventory Item"),
        db_index=True,
    )

    transaction_type = models.CharField(
        max_length=50,
        choices=TransactionType.choices,
        db_index=True,
        verbose_name=_("Transaction type"),
    )
    quantity = models.DecimalField(max_digits=14, decimal_places=2, verbose_name=_("Transaction quantity delta"))
    unit_cost = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Unit cost"))
    total_cost = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Total transaction cost value"))

    quantity_before = models.DecimalField(max_digits=14, decimal_places=2, verbose_name=_("Stock on hand quantity before transaction"))
    quantity_after = models.DecimalField(max_digits=14, decimal_places=2, verbose_name=_("Stock on hand quantity after transaction"))

    reference_number = models.CharField(max_length=100, blank=True, default="", db_index=True, verbose_name=_("External reference number"))
    reason = models.CharField(max_length=50, choices=AdjustmentReason.choices, blank=True, default="", verbose_name=_("Adjustment / Reason code"))

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="performed_inventory_transactions",
        null=True,
        blank=True,
        verbose_name=_("User who performed transaction"),
        db_index=True,
    )
    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Inventory Transaction"
        verbose_name_plural = "Inventory Transactions"
        indexes = [
            models.Index(fields=["tenant", "transaction_type"]),
            models.Index(fields=["tenant", "medicine", "created_at"]),
            models.Index(fields=["tenant", "warehouse", "created_at"]),
            models.Index(fields=["tenant", "batch"]),
        ]

    def __str__(self) -> str:
        return f"{self.get_transaction_type_display()}: {self.quantity} x {self.medicine.english_name} ({self.reference_number or 'No ref'})"
