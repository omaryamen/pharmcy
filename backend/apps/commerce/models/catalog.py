"""StoreProduct model linking Medicine Master Catalog entries to digital storefronts."""

from __future__ import annotations

from typing import Any
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.commerce.models.store import TenantStore


class StoreProduct(TenantAwareModel, FullAuditModel):
    """Digital product catalog entry publishing a Medicine to a TenantStore with commerce pricing & flags."""

    store = models.ForeignKey(
        TenantStore,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("Tenant Store"),
    )

    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.CASCADE,
        related_name="store_products",
        verbose_name=_("Medicine Master Item"),
    )

    display_name = models.CharField(max_length=200, verbose_name=_("Digital Display Name"))
    description = models.TextField(blank=True, default="", verbose_name=_("Product Description & Usage"))

    retail_price = models.DecimalField(max_digits=12, decimal_places=4, verbose_name=_("Online B2C Retail Price"))
    b2b_price = models.DecimalField(max_digits=12, decimal_places=4, verbose_name=_("Online B2B Wholesale Price"))

    is_published = models.BooleanField(default=True, verbose_name=_("Is Published Online"))
    is_featured = models.BooleanField(default=False, verbose_name=_("Is Featured Product"))
    is_prescription_required = models.BooleanField(default=False, verbose_name=_("Prescription Required for Purchase"))

    min_order_qty = models.IntegerField(default=1, verbose_name=_("Minimum Order Quantity"))
    max_order_qty = models.IntegerField(default=100, verbose_name=_("Maximum Order Quantity"))

    class Meta:
        db_table = "commerce_store_products"
        verbose_name = _("Store Product")
        verbose_name_plural = _("Store Products")
        constraints = [
            models.UniqueConstraint(
                fields=["store", "medicine"],
                name="commerce_store_medicine_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.display_name} ({self.retail_price} {self.store.currency})"
