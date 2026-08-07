"""Tenant model — the contract boundary of the multi-tenant SaaS platform."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel
from apps.common.models.managers import TenantManager


class TenantStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    TRIAL = "trial", _("Trial")
    SUSPENDED = "suspended", _("Suspended")
    INACTIVE = "inactive", _("Inactive")
    ARCHIVED = "archived", _("Archived")


class Tenant(BaseModel):
    """A contracted customer (pharmacy, chain, warehouse) with isolated data.

    Lifecycle is governed by ``status`` and soft-delete state.
    """

    name = models.CharField(max_length=150, verbose_name="Name")
    code = models.CharField(max_length=50, unique=True, verbose_name="Code")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_tenants",
        verbose_name="Owner",
    )
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

    def archive(self) -> None:
        self.status = TenantStatus.ARCHIVED
        self.is_active = False
        self.save(update_fields=["status", "is_active", "updated_at"])

    def restore(self) -> None:
        if self.is_deleted:
            self.is_deleted = False
            self.deleted_at = None
        self.status = TenantStatus.ACTIVE
        self.is_active = True
        self.save(update_fields=["status", "is_active", "is_deleted", "deleted_at", "updated_at"])

    def transfer_ownership(self, new_owner) -> None:
        self.owner = new_owner
        if new_owner and not self.users.filter(pk=new_owner.pk).exists():
            self.users.add(new_owner)
        self.save(update_fields=["owner", "updated_at"])

