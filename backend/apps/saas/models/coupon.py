"""Coupon, CouponRedemption, TenantCredit, and CreditTransaction models for SaaS discounts and credit ledger."""

from __future__ import annotations

from typing import Any
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.saas.models.enums import CouponDiscountType
from apps.saas.models.invoice import SaaSInvoice


class Coupon(FullAuditModel):
    """Promotional coupon discount for subscription plans."""

    code = models.CharField(max_length=60, unique=True, db_index=True, verbose_name=_("Coupon Code"))
    name = models.CharField(max_length=150, verbose_name=_("Coupon Name"))

    discount_type = models.CharField(
        max_length=20,
        choices=CouponDiscountType.choices,
        default=CouponDiscountType.PERCENTAGE,
        verbose_name=_("Discount Type"),
    )

    discount_value = models.DecimalField(max_digits=12, decimal_places=4, verbose_name=_("Discount Value"))
    currency = models.CharField(max_length=3, default="USD", verbose_name=_("Currency Code"))

    max_redemptions = models.IntegerField(default=-1, verbose_name=_("Max Redemptions (-1 for Unlimited)"))
    times_redeemed = models.IntegerField(default=0, verbose_name=_("Times Redeemed"))

    expiry_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Expiry Date"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    class Meta:
        db_table = "saas_coupons"
        verbose_name = _("Coupon")
        verbose_name_plural = _("Coupons")

    def __str__(self) -> str:
        return f"{self.code} - {self.name} ({self.discount_value} {self.discount_type})"


class CouponRedemption(TenantAwareModel, FullAuditModel):
    """Log of coupon redemptions per tenant and invoice."""

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name="redemptions",
        verbose_name=_("Coupon"),
    )

    invoice = models.ForeignKey(
        SaaSInvoice,
        on_delete=models.SET_NULL,
        related_name="coupon_redemptions",
        null=True,
        blank=True,
        verbose_name=_("SaaS Invoice"),
    )

    discount_applied = models.DecimalField(max_digits=12, decimal_places=4, verbose_name=_("Discount Amount Applied"))

    class Meta:
        db_table = "saas_coupon_redemptions"
        verbose_name = _("Coupon Redemption")
        verbose_name_plural = _("Coupon Redemptions")

    def __str__(self) -> str:
        return f"{self.tenant.name} redeemed {self.coupon.code} (-{self.discount_applied})"


class TenantCredit(TenantAwareModel, FullAuditModel):
    """Credit balance wallet held by a tenant for offsetting future invoices."""

    balance_amount = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name=_("Balance Amount"))
    currency = models.CharField(max_length=3, default="USD", verbose_name=_("Currency Code"))

    class Meta:
        db_table = "saas_tenant_credits"
        verbose_name = _("Tenant Credit Balance")
        verbose_name_plural = _("Tenant Credit Balances")

    def __str__(self) -> str:
        return f"{self.tenant.name} Credit Balance: {self.balance_amount} {self.currency}"


class CreditTransaction(TenantAwareModel, FullAuditModel):
    """Individual transaction entry on a tenant credit balance."""

    tenant_credit = models.ForeignKey(
        TenantCredit,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name=_("Tenant Credit"),
    )

    amount = models.DecimalField(max_digits=12, decimal_places=4, verbose_name=_("Transaction Amount"))
    transaction_type = models.CharField(max_length=30, verbose_name=_("Transaction Type (grant, usage, refund)"))
    description = models.CharField(max_length=255, verbose_name=_("Transaction Description"))

    invoice = models.ForeignKey(
        SaaSInvoice,
        on_delete=models.SET_NULL,
        related_name="credit_transactions",
        null=True,
        blank=True,
        verbose_name=_("SaaS Invoice"),
    )

    class Meta:
        db_table = "saas_credit_transactions"
        verbose_name = _("Credit Transaction")
        verbose_name_plural = _("Credit Transactions")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.tenant.name} Credit {self.transaction_type}: {self.amount}"
