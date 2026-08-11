"""Supplier product pricing and contract terms model."""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel


class SupplierProductPrice(TenantAwareModel, FullAuditModel):
    """Supplier-specific product pricing, contract agreements, lead times, and min/max ordering constraints."""

    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.CASCADE,
        related_name="product_prices",
        verbose_name=_("Supplier"),
        db_index=True,
    )
    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.CASCADE,
        related_name="supplier_prices",
        verbose_name=_("Medicine"),
        db_index=True,
    )

    supplier_sku = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Supplier SKU"))
    supplier_barcode = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Supplier Barcode"))

    last_purchase_price = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Last Purchase Price"))
    current_contract_price = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Current Contract Price"))

    minimum_order_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("1.0000"), verbose_name=_("Minimum Order Quantity"))
    maximum_order_quantity = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True, verbose_name=_("Maximum Order Quantity"))

    is_preferred_supplier = models.BooleanField(default=False, verbose_name=_("Is Preferred Supplier"))
    lead_time_days = models.PositiveIntegerField(default=3, verbose_name=_("Lead Time (Days)"))

    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))
    effective_date = models.DateField(null=True, blank=True, verbose_name=_("Effective Date"))
    expiry_date = models.DateField(null=True, blank=True, verbose_name=_("Contract Expiry Date"))

    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))
    is_active = models.BooleanField(default=True, db_index=True, verbose_name=_("Is Active"))

    class Meta:
        db_table = "procurement_supplier_prices"
        verbose_name = _("Supplier Product Price")
        verbose_name_plural = _("Supplier Product Prices")
        ordering = ["supplier", "medicine"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "supplier", "medicine"],
                name="supplier_product_price_tenant_uniq",
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "supplier"]),
            models.Index(fields=["tenant", "medicine"]),
            models.Index(fields=["tenant", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.supplier.name} - {self.medicine.english_name} ({self.current_contract_price} {self.currency})"
