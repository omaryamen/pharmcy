"""Customer Medical Profile Model supporting secure pharmacy medical foundation."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel
from apps.customers.models.enums import BloodType


class CustomerMedicalProfile(FullAuditModel, TenantAwareModel):
    """Secure customer medical foundation for future clinical pharmacy operations."""

    customer = models.OneToOneField(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="medical_profile",
        verbose_name=_("Customer"),
    )
    blood_type = models.CharField(
        max_length=10,
        choices=BloodType.choices,
        default=BloodType.UNKNOWN,
        verbose_name=_("Blood type"),
    )
    allergies = models.JSONField(default=list, blank=True, verbose_name=_("Allergies list"))
    chronic_conditions = models.JSONField(default=list, blank=True, verbose_name=_("Chronic conditions list"))

    emergency_contact_name = models.CharField(max_length=150, blank=True, default="", verbose_name=_("Emergency contact name"))
    emergency_contact_phone = models.CharField(max_length=32, blank=True, default="", verbose_name=_("Emergency contact phone"))
    emergency_contact_relationship = models.CharField(
        max_length=50, blank=True, default="", verbose_name=_("Emergency contact relationship")
    )

    medical_notes = models.TextField(blank=True, default="", verbose_name=_("Medical notes"))
    preferred_physician = models.CharField(max_length=150, blank=True, default="", verbose_name=_("Preferred physician"))
    preferred_pharmacy = models.CharField(max_length=150, blank=True, default="", verbose_name=_("Preferred pharmacy"))
    insurance_info_notes = models.TextField(blank=True, default="", verbose_name=_("Insurance notes"))

    class Meta:
        verbose_name = "Customer Medical Profile"
        verbose_name_plural = "Customer Medical Profiles"
        indexes = [
            models.Index(fields=["tenant", "customer"]),
        ]

    def __str__(self) -> str:
        return f"Medical Profile - {self.customer.code}"
