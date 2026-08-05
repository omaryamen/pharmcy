"""Tenant model — the contract boundary of the multi-tenant SaaS platform."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import UUIDTimeStampedModel
from apps.common.models.managers import TenantManager


class TenantStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    TRIAL = "trial", _("Trial")
    SUSPENDED = "suspended", _("Suspended")
    INACTIVE = "inactive", _("Inactive")


class Tenant(UUIDTimeStampedModel):
    """A contracted customer (pharmacy, chain, warehouse) with isolated data.

    Lifecycle is governed by ``status``; tenants are never hard-deleted.
    """

    name = models.CharField(max_length=150, verbose_name="Name")
    code = models.CharField(max_length=50, unique=True, verbose_name="Code")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    status = models.CharField(
        max_length=20,
        choices=TenantStatus.choices,
        default=TenantStatus.TRIAL,
        db_index=True,
        verbose_name="Status",
    )
    timezone = models.CharField(max_length=64, default="UTC", verbose_name="Timezone")
    locale = models.CharField(max_length=10, default="en", verbose_name="Locale")
    subscription_tier = models.CharField(max_length=50, default="trial", verbose_name="Subscription tier")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="Active")
    meta = models.JSONField(default=dict, blank=True, verbose_name="Meta")

    objects = TenantManager()

    class Meta:
        ordering = ["name"]
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"

    def __str__(self) -> str:
        return self.name

    def activate(self) -> None:
        self.status = TenantStatus.ACTIVE
        self.is_active = True
        self.save(update_fields=["status", "is_active", "updated_at"])

    def suspend(self) -> None:
        self.status = TenantStatus.SUSPENDED
        self.is_active = False
        self.save(update_fields=["status", "is_active", "updated_at"])

    def deactivate(self) -> None:
        self.status = TenantStatus.INACTIVE
        self.is_active = False
        self.save(update_fields=["status", "is_active", "updated_at"])
