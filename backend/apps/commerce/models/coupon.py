"""StoreCoupon model for online storefront promotional discount codes."""

from __future__ import annotations

from typing import Any
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.commerce.models.enums import CouponDiscountType
from apps.commerce.models.store import TenantStore


class StoreCoupon(TenantAwareModel, FullAuditModel):
    """Promotional discount code applicable at storefront checkout."""

    store = models.ForeignKey(
        TenantStore,
        on_delete=models.CASCADE,
        related_name="coupons",
        verbose_name=_("Tenant Store"),
    )

    code = models.CharField(max_length=60, db_index=True, verbose_name=_("Coupon Code"))
    discount_type = models.CharField(
        max_length=20,
        choices=CouponDiscountType.choices,
        default=CouponDiscountType.PERCENTAGE,
        verbose_name=_("Discount Type"),
    )

    discount_value = models.DecimalField(max_digits=12, decimal_places=4, verbose_name=_("Discount Value"))
    min_order_amount = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name=_("Minimum Order Subtotal"))

    usage_limit = models.IntegerField(default=-1, verbose_name=_("Total Usage Limit (-1 for Unlimited)"))
    times_used = models.IntegerField(default=0, verbose_name=_("Times Used"))

    expires_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Expiry Timestamp"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    class Meta:
        db_table = "commerce_store_coupons"
        verbose_name = _("Store Coupon")
        verbose_name_plural = _("Store Coupons")
        constraints = [
            models.UniqueConstraint(
                fields=["store", "code"],
                name="commerce_store_coupon_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.code} ({self.discount_value} {self.discount_type}) - {self.store.name}"

    @property
    def is_valid_now(self) -> bool:
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        if self.usage_limit != -1 and self.times_used >= self.usage_limit:
            return False
        return True
