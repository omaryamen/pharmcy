"""Pharmaceutical Batch/Lot entity representing specific manufactured medication lots."""

from __future__ import annotations

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel
from apps.inventory.models.enums import BatchStatus
from apps.inventory.validators import validate_batch_dates


class Batch(FullAuditModel, TenantAwareModel):
    """Pharmaceutical Batch/Lot Entity with manufacturing date, expiry, costing, and compliance status."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="batches",
        verbose_name=_("Company"),
        db_index=True,
    )
    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.CASCADE,
        related_name="batches",
        verbose_name=_("Medicine"),
        db_index=True,
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.SET_NULL,
        related_name="batches",
        null=True,
        blank=True,
        verbose_name=_("Supplier"),
        db_index=True,
    )

    batch_number = models.CharField(max_length=100, db_index=True, verbose_name=_("Batch number"))
    lot_number = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Lot number"))

    manufacturing_date = models.DateField(null=True, blank=True, verbose_name=_("Manufacturing date"))
    expiry_date = models.DateField(db_index=True, verbose_name=_("Expiry date"))

    registration_number = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Regulatory registration number"))
    country_of_origin = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Country of origin"))

    status = models.CharField(
        max_length=30,
        choices=BatchStatus.choices,
        default=BatchStatus.ACTIVE,
        db_index=True,
        verbose_name=_("Batch status"),
    )

    unit_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0.0000, verbose_name=_("Purchase unit cost"))
    selling_price = models.DecimalField(max_digits=14, decimal_places=4, default=0.0000, verbose_name=_("Suggested selling price"))

    initial_quantity = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name=_("Initial received quantity"))
    current_quantity = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name=_("Current batch total quantity"))

    storage_requirements = models.TextField(blank=True, default="", verbose_name=_("Storage requirements"))
    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        ordering = ["expiry_date", "batch_number"]
        verbose_name = "Batch / Lot"
        verbose_name_plural = "Batches / Lots"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "medicine", "batch_number"], name="inventory_batch_tenant_med_batch_uniq"),
        ]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "medicine", "expiry_date"]),
            models.Index(fields=["tenant", "expiry_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.medicine.english_name} (Batch: {self.batch_number}, Exp: {self.expiry_date})"

    @property
    def is_expired(self) -> bool:
        if not self.expiry_date:
            return False
        return self.expiry_date < timezone.now().date()

    def clean(self) -> None:
        super().clean()
        validate_batch_dates(self.manufacturing_date, self.expiry_date)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def block(self) -> None:
        self.status = BatchStatus.BLOCKED
        self.save(update_fields=["status", "updated_at"])

    def unblock(self) -> None:
        self.status = BatchStatus.ACTIVE
        self.save(update_fields=["status", "updated_at"])

    def recall(self) -> None:
        self.status = BatchStatus.RECALLED
        self.save(update_fields=["status", "updated_at"])
