"""StockMovement entity model."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel
from apps.stock_movement.models.enums import MovementStatus, MovementType, ReferenceType


class StockMovement(FullAuditModel, TenantAwareModel):
    """Central authoritative stock movement document representing physical inventory quantity changes."""

    movement_number = models.CharField(
        max_length=60,
        db_index=True,
        verbose_name=_("Movement number"),
        help_text=_("System generated movement code e.g. STK-2026-000001"),
    )
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="stock_movements",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="stock_movements",
        null=True,
        blank=True,
        verbose_name=_("Branch"),
        db_index=True,
    )
    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.CASCADE,
        related_name="stock_movements",
        verbose_name=_("Primary Warehouse"),
        db_index=True,
    )
    source_warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.SET_NULL,
        related_name="source_stock_movements",
        null=True,
        blank=True,
        verbose_name=_("Source Warehouse"),
        db_index=True,
    )
    destination_warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.SET_NULL,
        related_name="destination_stock_movements",
        null=True,
        blank=True,
        verbose_name=_("Destination Warehouse"),
        db_index=True,
    )
    source_location = models.ForeignKey(
        "warehouses.StorageLocation",
        on_delete=models.SET_NULL,
        related_name="source_stock_movements",
        null=True,
        blank=True,
        verbose_name=_("Source Location"),
        db_index=True,
    )
    destination_location = models.ForeignKey(
        "warehouses.StorageLocation",
        on_delete=models.SET_NULL,
        related_name="destination_stock_movements",
        null=True,
        blank=True,
        verbose_name=_("Destination Location"),
        db_index=True,
    )

    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.SET_NULL,
        related_name="stock_movements",
        null=True,
        blank=True,
        verbose_name=_("Medicine Header"),
        db_index=True,
    )
    batch = models.ForeignKey(
        "inventory.Batch",
        on_delete=models.SET_NULL,
        related_name="stock_movements",
        null=True,
        blank=True,
        verbose_name=_("Batch Header"),
        db_index=True,
    )

    movement_type = models.CharField(
        max_length=50,
        choices=MovementType.choices,
        db_index=True,
        verbose_name=_("Movement type"),
    )
    movement_status = models.CharField(
        max_length=30,
        choices=MovementStatus.choices,
        default=MovementStatus.DRAFT,
        db_index=True,
        verbose_name=_("Movement status"),
    )

    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Total movement quantity"),
    )
    unit_of_measure = models.CharField(
        max_length=30,
        default="Pcs",
        blank=True,
        verbose_name=_("Unit of measure"),
    )
    unit_cost = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal("0.0000"),
        verbose_name=_("Unit cost"),
    )
    total_cost = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal("0.0000"),
        verbose_name=_("Total cost value"),
    )

    reference_type = models.CharField(
        max_length=50,
        choices=ReferenceType.choices,
        blank=True,
        default="",
        verbose_name=_("Reference document type"),
    )
    reference_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
        db_index=True,
        verbose_name=_("External reference ID"),
    )
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        default="",
        db_index=True,
        verbose_name=_("External reference code"),
    )

    reason = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name=_("Movement reason"),
    )
    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="performed_stock_movements",
        null=True,
        blank=True,
        verbose_name=_("User who performed movement"),
        db_index=True,
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_stock_movements",
        null=True,
        blank=True,
        verbose_name=_("User who approved movement"),
        db_index=True,
    )

    reversed_movement = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reversals",
        verbose_name=_("Original movement reversed"),
        db_index=True,
    )
    is_reversal = models.BooleanField(
        default=False,
        verbose_name=_("Is compensating reversal movement"),
    )

    idempotency_key = models.CharField(
        max_length=100,
        blank=True,
        default="",
        db_index=True,
        verbose_name=_("Idempotency key"),
        help_text=_("Unique key to prevent duplicate processing"),
    )

    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Completed timestamp"))
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Cancelled timestamp"))

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Stock Movement"
        verbose_name_plural = "Stock Movements"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "movement_number"],
                name="stock_movement_tenant_number_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "movement_type"]),
            models.Index(fields=["tenant", "movement_status"]),
            models.Index(fields=["tenant", "created_at"]),
            models.Index(fields=["tenant", "idempotency_key"]),
            models.Index(fields=["reference_type", "reference_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.movement_number} [{self.get_movement_type_display()}] - {self.get_movement_status_display()}"

    def mark_completed(self, user=None) -> None:
        self.movement_status = MovementStatus.COMPLETED
        self.completed_at = timezone.now()
        if user and not self.performed_by:
            self.performed_by = user
        self.save(update_fields=["movement_status", "completed_at", "performed_by", "updated_at"])

    def mark_cancelled(self, user=None) -> None:
        self.movement_status = MovementStatus.CANCELLED
        self.cancelled_at = timezone.now()
        self.save(update_fields=["movement_status", "cancelled_at", "updated_at"])
