"""Prescription header and line item domain models."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.prescriptions.models.enums import (
    PrescriptionLineStatus,
    PrescriptionStatus,
    PrescriptionType,
)


class Prescription(TenantAwareModel, FullAuditModel):
    """Header document representing a medical prescription."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="prescriptions",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.PROTECT,
        related_name="prescriptions",
        verbose_name=_("Branch"),
        db_index=True,
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="prescriptions",
        verbose_name=_("Patient / Customer"),
        db_index=True,
    )

    rx_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Prescription Number (RX)"))
    rx_date = models.DateField(verbose_name=_("Prescription Date"), db_index=True)
    expiry_date = models.DateField(verbose_name=_("Prescription Expiry Date"), db_index=True)

    status = models.CharField(
        max_length=30,
        choices=PrescriptionStatus.choices,
        default=PrescriptionStatus.DRAFT,
        db_index=True,
        verbose_name=_("Prescription Status"),
    )
    rx_type = models.CharField(
        max_length=30,
        choices=PrescriptionType.choices,
        default=PrescriptionType.REGULAR,
        db_index=True,
        verbose_name=_("Prescription Classification"),
    )

    doctor_name = models.CharField(max_length=200, verbose_name=_("Prescribing Doctor Name"))
    doctor_license_number = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Doctor License / Registration Number"))
    clinic_hospital_name = models.CharField(max_length=200, blank=True, default="", verbose_name=_("Clinic / Hospital Name"))

    diagnosis_code = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Diagnosis Code (ICD-10 / Text)"))
    diagnosis_description = models.TextField(blank=True, default="", verbose_name=_("Diagnosis Description"))

    is_verified = models.BooleanField(default=False, verbose_name=_("Is Clinically Verified"))
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="verified_prescriptions",
        null=True,
        blank=True,
        verbose_name=_("Verified By Pharmacist"),
    )
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Verified At"))

    dispensed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Fully Dispensed At"))
    dispensed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="dispensed_prescriptions",
        null=True,
        blank=True,
        verbose_name=_("Dispensed By Pharmacist"),
    )

    idempotency_key = models.CharField(max_length=100, blank=True, default="", db_index=True, verbose_name=_("Idempotency Key"))
    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        db_table = "prescriptions"
        verbose_name = _("Prescription")
        verbose_name_plural = _("Prescriptions")
        ordering = ["-rx_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "rx_number"],
                name="prescription_tenant_number_uniq",
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "customer"]),
            models.Index(fields=["tenant", "rx_type"]),
        ]

    def __str__(self) -> str:
        return f"{self.rx_number} - {self.customer.english_name} [{self.status}]"


class PrescriptionLine(TenantAwareModel, FullAuditModel):
    """Line item inside a Prescription representing prescribed medicine and instructions."""

    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name=_("Prescription"),
        db_index=True,
    )
    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.PROTECT,
        related_name="prescription_lines",
        verbose_name=_("Prescribed Medicine"),
    )

    prescribed_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("1.0000"), verbose_name=_("Prescribed Quantity"))
    dispensed_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Dispensed Quantity"))

    dosage = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Dosage (e.g. 500mg)"))
    frequency = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Frequency (e.g. 3 times daily)"))
    duration_days = models.PositiveIntegerField(default=1, verbose_name=_("Duration in Days"))
    instructions = models.TextField(blank=True, default="", verbose_name=_("Usage / Patient Instructions"))

    refills_allowed = models.PositiveIntegerField(default=0, verbose_name=_("Refills Allowed"))
    refills_remaining = models.PositiveIntegerField(default=0, verbose_name=_("Refills Remaining"))

    status = models.CharField(
        max_length=30,
        choices=PrescriptionLineStatus.choices,
        default=PrescriptionLineStatus.PENDING,
        verbose_name=_("Line Dispensing Status"),
    )

    is_substituted = models.BooleanField(default=False, verbose_name=_("Is Generic Substituted"))
    substituted_medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.SET_NULL,
        related_name="substituted_prescription_lines",
        null=True,
        blank=True,
        verbose_name=_("Substituted Medicine"),
    )
    substitution_reason = models.CharField(max_length=250, blank=True, default="", verbose_name=_("Substitution Reason"))

    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        db_table = "prescription_lines"
        verbose_name = _("Prescription Line")
        verbose_name_plural = _("Prescription Lines")
        ordering = ["created_at"]
