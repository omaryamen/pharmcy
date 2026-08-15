"""CommerceOrder and CommerceOrderLine models for online digital orders."""

from __future__ import annotations

from typing import Any
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.commerce.models.catalog import StoreProduct
from apps.commerce.models.enums import CommerceOrderStatus, CommercePaymentStatus, DeliveryMethod
from apps.commerce.models.store import TenantStore


class CommerceOrder(TenantAwareModel, FullAuditModel):
    """Digital commercial order placed through online B2C or B2B storefronts."""

    order_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Order Number (ORD)"))

    store = models.ForeignKey(
        TenantStore,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name=_("Tenant Store"),
    )

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="commerce_orders",
        verbose_name=_("Customer"),
    )

    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="commerce_orders",
        null=True,
        blank=True,
        verbose_name=_("Fulfillment Branch"),
    )

    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.SET_NULL,
        related_name="commerce_orders",
        null=True,
        blank=True,
        verbose_name=_("Fulfillment Warehouse"),
    )

    status = models.CharField(
        max_length=30,
        choices=CommerceOrderStatus.choices,
        default=CommerceOrderStatus.PENDING,
        db_index=True,
        verbose_name=_("Order Status"),
    )

    payment_status = models.CharField(
        max_length=30,
        choices=CommercePaymentStatus.choices,
        default=CommercePaymentStatus.PENDING,
        db_index=True,
        verbose_name=_("Payment Status"),
    )

    delivery_method = models.CharField(
        max_length=30,
        choices=DeliveryMethod.choices,
        default=DeliveryMethod.STANDARD_DELIVERY,
        verbose_name=_("Delivery Method"),
    )

    subtotal = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name=_("Subtotal Amount"))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name=_("Discount Amount"))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name=_("Tax Amount"))
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name=_("Shipping Fee"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name=_("Grand Total Amount"))

    currency = models.CharField(max_length=3, default="USD", verbose_name=_("Currency Code"))
    shipping_address = models.TextField(blank=True, default="", verbose_name=_("Shipping Address"))
    idempotency_key = models.CharField(max_length=120, blank=True, default="", db_index=True, verbose_name=_("Idempotency Key"))

    notes = models.TextField(blank=True, default="", verbose_name=_("Customer Notes"))

    class Meta:
        db_table = "commerce_orders"
        verbose_name = _("Commerce Order")
        verbose_name_plural = _("Commerce Orders")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.order_number} - {self.customer} [{self.total_amount} {self.currency}] ({self.status})"


class CommerceOrderLine(TenantAwareModel, FullAuditModel):
    """Line item on an online commerce order with exact price and tax snapshot."""

    order = models.ForeignKey(
        CommerceOrder,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name=_("Commerce Order"),
    )

    product = models.ForeignKey(
        StoreProduct,
        on_delete=models.PROTECT,
        related_name="order_lines",
        verbose_name=_("Store Product"),
    )

    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.PROTECT,
        related_name="commerce_lines",
        verbose_name=_("Medicine Master Item"),
    )

    quantity = models.DecimalField(max_digits=12, decimal_places=4, default=1, verbose_name=_("Order Quantity"))
    unit_price = models.DecimalField(max_digits=12, decimal_places=4, verbose_name=_("Unit Price Snapshot"))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name=_("Discount Amount"))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name=_("Tax Amount"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=4, verbose_name=_("Total Line Amount"))

    class Meta:
        db_table = "commerce_order_lines"
        verbose_name = _("Commerce Order Line")
        verbose_name_plural = _("Commerce Order Lines")

    def __str__(self) -> str:
        return f"{self.order.order_number} Line: {self.product.display_name} x {self.quantity}"
