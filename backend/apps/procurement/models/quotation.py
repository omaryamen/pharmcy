"""Supplier Quotation foundation model."""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel


class SupplierQuotationStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    SUBMITTED = "submitted", _("Submitted")
    ACCEPTED = "accepted", _("Accepted")
    REJECTED = "rejected", _("Rejected")
    EXPIRED = "expired", _("Expired")


class SupplierQuotation(TenantAwareModel, FullAuditModel):
    """Supplier Quotation document foundation."""

    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.CASCADE,
        related_name="quotations",
        verbose_name=_("Supplier"),
        db_index=True,
    )
    quotation_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Quotation Number"))
    validity_date = models.DateField(null=True, blank=True, verbose_name=_("Validity Date"))
    status = models.CharField(
        max_length=30,
        choices=SupplierQuotationStatus.choices,
        default=SupplierQuotationStatus.DRAFT,
        db_index=True,
        verbose_name=_("Status"),
    )
    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        db_table = "procurement_supplier_quotations"
        verbose_name = _("Supplier Quotation")
        verbose_name_plural = _("Supplier Quotations")
        ordering = ["-created_at"]


class SupplierQuotationLine(TenantAwareModel, FullAuditModel):
    """Individual item inside a SupplierQuotation."""

    quotation = models.ForeignKey(
        SupplierQuotation,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name=_("Supplier Quotation"),
        db_index=True,
    )
    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.PROTECT,
        related_name="quotation_lines",
        verbose_name=_("Medicine"),
        db_index=True,
    )
    quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("1.0000"), verbose_name=_("Quantity"))
    unit_price = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Unit Price"))
    discount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Discount"))
    tax = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Tax"))
    lead_time_days = models.PositiveIntegerField(default=3, verbose_name=_("Lead Time Days"))

    class Meta:
        db_table = "procurement_supplier_quotation_lines"
        verbose_name = _("Supplier Quotation Line")
        verbose_name_plural = _("Supplier Quotation Lines")
