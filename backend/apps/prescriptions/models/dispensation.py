"""PrescriptionDispense and PrescriptionDispenseLine models for dispensing logs."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.prescriptions.models.enums import DispenseStatus


class PrescriptionDispense(TenantAwareModel, FullAuditModel):
    """Record representing a physical prescription dispensing event at the pharmacy."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="prescription_dispensations",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.PROTECT,
        related_name="prescription_dispensations",
        verbose_name=_("Branch"),
        db_index=True,
    )
    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.PROTECT,
        related_name="prescription_dispensations",
        verbose_name=_("Warehouse"),
        db_index=True,
    )
    prescription = models.ForeignKey(
        "prescriptions.Prescription",
        on_delete=models.PROTECT,
        related_name="dispensations",
        verbose_name=_("Prescription"),
        db_index=True,
    )
    sales_invoice = models.ForeignKey(
        "sales.SalesInvoice",
        on_delete=models.SET_NULL,
        related_name="prescription_dispensations",
        null=True,
        blank=True,
        verbose_name=_("Linked POS Sales Invoice"),
    )

    dispense_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Dispensation Number (DISP)"))
    dispensed_at = models.DateTimeField(verbose_name=_("Dispensed At"), db_index=True)

    status = models.CharField(
        max_length=30,
        choices=DispenseStatus.choices,
        default=DispenseStatus.COMPLETED,
        db_index=True,
        verbose_name=_("Dispense Status"),
    )

    dispensed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="executed_prescription_dispensations",
        null=True,
        blank=True,
        verbose_name=_("Dispensed By Pharmacist"),
    )

    pharmacist_notes = models.TextField(blank=True, default="", verbose_name=_("Pharmacist Dispensing Notes"))

    class Meta:
        db_table = "prescription_dispensations"
        verbose_name = _("Prescription Dispensation")
        verbose_name_plural = _("Prescription Dispensations")
        ordering = ["-dispensed_at", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "dispense_number"],
                name="prescription_dispense_tenant_number_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.dispense_number} - RX {self.prescription.rx_number}"


class PrescriptionDispenseLine(TenantAwareModel, FullAuditModel):
    """Line item detailing specific medicine batch dispensed."""

    dispense = models.ForeignKey(
        PrescriptionDispense,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name=_("Dispense Header"),
        db_index=True,
    )
    prescription_line = models.ForeignKey(
        "prescriptions.PrescriptionLine",
        on_delete=models.PROTECT,
        related_name="dispense_lines",
        verbose_name=_("Original Prescription Line"),
    )
    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.PROTECT,
        related_name="dispense_lines",
        verbose_name=_("Dispensed Medicine"),
    )
    batch = models.ForeignKey(
        "inventory.Batch",
        on_delete=models.PROTECT,
        related_name="dispense_lines",
        verbose_name=_("Dispensed Batch"),
    )
    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.PROTECT,
        related_name="dispense_lines",
        verbose_name=_("Warehouse"),
    )
    storage_location = models.ForeignKey(
        "warehouses.StorageLocation",
        on_delete=models.PROTECT,
        related_name="dispense_lines",
        verbose_name=_("Storage Location"),
    )

    dispensed_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("1.0000"), verbose_name=_("Dispensed Quantity"))
    unit_price = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Selling Unit Price"))
    total_price = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Line Total Price"))

    class Meta:
        db_table = "prescription_dispense_lines"
        verbose_name = _("Prescription Dispense Line")
        verbose_name_plural = _("Prescription Dispense Lines")
        ordering = ["created_at"]
