"""Warehouse Model representing physical and virtual pharmaceutical storage entities."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel
from apps.warehouses.models.enums import WarehouseStatus, WarehouseType


class Warehouse(FullAuditModel, TenantAwareModel):
    """Enterprise Warehouse Entity belonging to Company, Branch, and Tenant."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="warehouses",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="warehouses",
        null=True,
        blank=True,
        verbose_name=_("Branch"),
        db_index=True,
    )

    code = models.CharField(max_length=50, verbose_name=_("Warehouse code"))
    name = models.CharField(max_length=255, verbose_name=_("Warehouse name"))
    arabic_name = models.CharField(max_length=255, blank=True, default="", verbose_name=_("Arabic name"))
    english_name = models.CharField(max_length=255, blank=True, default="", verbose_name=_("English name"))
    description = models.TextField(blank=True, default="", verbose_name=_("Description"))

    warehouse_type = models.CharField(
        max_length=50,
        choices=WarehouseType.choices,
        default=WarehouseType.MAIN,
        db_index=True,
        verbose_name=_("Warehouse type"),
    )
    status = models.CharField(
        max_length=30,
        choices=WarehouseStatus.choices,
        default=WarehouseStatus.ACTIVE,
        db_index=True,
        verbose_name=_("Status"),
    )

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="managed_warehouses",
        null=True,
        blank=True,
        verbose_name=_("Warehouse manager"),
        db_index=True,
    )

    # Contact & Geolocation
    phone = models.CharField(max_length=32, blank=True, default="", verbose_name=_("Phone"))
    email = models.EmailField(blank=True, default="", verbose_name=_("Email"))
    address = models.CharField(max_length=255, blank=True, default="", verbose_name=_("Address"))
    country = models.CharField(max_length=100, default="Yemen", verbose_name=_("Country"))
    city = models.CharField(max_length=100, default="Sanaa", verbose_name=_("City"))
    district = models.CharField(max_length=100, blank=True, default="", verbose_name=_("District"))
    postal_code = models.CharField(max_length=20, blank=True, default="", verbose_name=_("Postal code"))
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True, verbose_name=_("Latitude"))
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True, verbose_name=_("Longitude"))
    working_hours = models.CharField(max_length=255, blank=True, default="", verbose_name=_("Working hours"))

    # Default Roles
    is_default_receiving = models.BooleanField(default=False, verbose_name=_("Is default receiving warehouse"))
    is_default_returns = models.BooleanField(default=False, verbose_name=_("Is default returns warehouse"))
    is_default_quarantine = models.BooleanField(default=False, verbose_name=_("Is default quarantine warehouse"))
    is_default_damaged = models.BooleanField(default=False, verbose_name=_("Is default damaged warehouse"))
    is_default_cold = models.BooleanField(default=False, verbose_name=_("Is default cold storage warehouse"))

    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        ordering = ["name"]
        verbose_name = "Warehouse"
        verbose_name_plural = "Warehouses"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code"], name="warehouses_warehouse_tenant_code_uniq"),
            models.UniqueConstraint(fields=["tenant", "company", "name"], name="warehouses_warehouse_tenant_company_name_uniq"),
        ]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "warehouse_type"]),
            models.Index(fields=["tenant", "company"]),
            models.Index(fields=["tenant", "branch"]),
        ]

    def __str__(self) -> str:
        return f"{self.display_name} ({self.code})"

    @property
    def display_name(self) -> str:
        if self.arabic_name:
            return self.arabic_name
        if self.english_name:
            return self.english_name
        return self.name

    def activate(self) -> None:
        self.status = WarehouseStatus.ACTIVE
        self.save(update_fields=["status", "updated_at"])

    def deactivate(self) -> None:
        self.status = WarehouseStatus.INACTIVE
        self.save(update_fields=["status", "updated_at"])

    def suspend(self) -> None:
        self.status = WarehouseStatus.SUSPENDED
        self.save(update_fields=["status", "updated_at"])

    def close_temporarily(self) -> None:
        self.status = WarehouseStatus.TEMPORARILY_CLOSED
        self.save(update_fields=["status", "updated_at"])

    def restore(self) -> None:
        if self.is_deleted:
            self.is_deleted = False
            self.deleted_at = None
        self.status = WarehouseStatus.ACTIVE
        self.save(update_fields=["status", "is_deleted", "deleted_at", "updated_at"])
