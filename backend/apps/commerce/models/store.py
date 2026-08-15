"""TenantStore model configuring multi-tenant digital pharmacy storefronts."""

from __future__ import annotations

from typing import Any
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.commerce.models.enums import StoreStatus


class TenantStore(TenantAwareModel, FullAuditModel):
    """Digital storefront portal configuration for a multi-tenant pharmacy."""

    code = models.CharField(max_length=60, db_index=True, verbose_name=_("Store Code"))
    name = models.CharField(max_length=150, verbose_name=_("Storefront Display Name"))
    domain = models.CharField(max_length=255, blank=True, default="", verbose_name=_("Custom Domain or Subdomain"))
    logo_url = models.URLField(max_length=500, blank=True, default="", verbose_name=_("Brand Logo URL"))

    currency = models.CharField(max_length=3, default="USD", verbose_name=_("Store Currency Code"))
    status = models.CharField(
        max_length=20,
        choices=StoreStatus.choices,
        default=StoreStatus.ACTIVE,
        verbose_name=_("Storefront Status"),
    )

    is_b2b_enabled = models.BooleanField(default=True, verbose_name=_("Enable B2B Wholesale Commerce"))
    is_b2c_enabled = models.BooleanField(default=True, verbose_name=_("Enable B2C Retail Commerce"))

    delivery_fee = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name=_("Standard Delivery Fee"))
    free_delivery_threshold = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name=_("Free Delivery Threshold"))

    class Meta:
        db_table = "commerce_tenant_stores"
        verbose_name = _("Tenant Store")
        verbose_name_plural = _("Tenant Stores")
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "code"],
                name="commerce_store_tenant_code_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.code}) - {self.tenant.name}"
