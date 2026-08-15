"""Cart and CartItem models for guest and customer shopping carts."""

from __future__ import annotations

from typing import Any
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.commerce.models.catalog import StoreProduct
from apps.commerce.models.store import TenantStore


class Cart(TenantAwareModel, FullAuditModel):
    """Shopping cart entity supporting both guest sessions and authenticated customer profiles."""

    store = models.ForeignKey(
        TenantStore,
        on_delete=models.CASCADE,
        related_name="carts",
        verbose_name=_("Tenant Store"),
    )

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="carts",
        null=True,
        blank=True,
        verbose_name=_("Customer Profile"),
    )

    session_key = models.CharField(max_length=100, blank=True, default="", db_index=True, verbose_name=_("Guest Session Key"))
    currency = models.CharField(max_length=3, default="USD", verbose_name=_("Currency Code"))

    class Meta:
        db_table = "commerce_carts"
        verbose_name = _("Shopping Cart")
        verbose_name_plural = _("Shopping Carts")

    def __str__(self) -> str:
        return f"Cart #{self.pk} ({self.customer or self.session_key})"


class CartItem(TenantAwareModel, FullAuditModel):
    """Individual product line item in a shopping cart."""

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Shopping Cart"),
    )

    product = models.ForeignKey(
        StoreProduct,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name=_("Store Product"),
    )

    quantity = models.DecimalField(max_digits=12, decimal_places=4, default=1, verbose_name=_("Item Quantity"))
    unit_price = models.DecimalField(max_digits=12, decimal_places=4, verbose_name=_("Unit Price Snapshot"))

    class Meta:
        db_table = "commerce_cart_items"
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"],
                name="commerce_cart_product_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.product.display_name} x {self.quantity}"
