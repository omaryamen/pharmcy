"""Storage Location Model representing hierarchical storage structures within a Warehouse."""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel
from apps.warehouses.models.enums import LocationStatus, LocationType
from apps.warehouses.validators import validate_location_hierarchy


class StorageLocation(FullAuditModel, TenantAwareModel):
    """Hierarchical Storage Location Entity (Zone, Aisle, Rack, Shelf, Bin, Cabinet, Freezer, etc.)."""

    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.CASCADE,
        related_name="locations",
        verbose_name=_("Warehouse"),
        db_index=True,
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        null=True,
        blank=True,
        verbose_name=_("Parent location"),
        db_index=True,
    )

    code = models.CharField(max_length=50, verbose_name=_("Location code"))
    name = models.CharField(max_length=255, verbose_name=_("Location name"))
    arabic_name = models.CharField(max_length=255, blank=True, default="", verbose_name=_("Arabic name"))
    english_name = models.CharField(max_length=255, blank=True, default="", verbose_name=_("English name"))
    description = models.TextField(blank=True, default="", verbose_name=_("Description"))

    location_type = models.CharField(
        max_length=50,
        choices=LocationType.choices,
        default=LocationType.ZONE,
        db_index=True,
        verbose_name=_("Location type"),
    )
    status = models.CharField(
        max_length=30,
        choices=LocationStatus.choices,
        default=LocationStatus.ACTIVE,
        db_index=True,
        verbose_name=_("Status"),
    )

    display_order = models.PositiveIntegerField(default=0, verbose_name=_("Display order"))

    # Capacity & Utilization Foundation
    capacity = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name=_("Maximum capacity"))
    capacity_unit = models.CharField(max_length=50, default="units", blank=True, verbose_name=_("Capacity unit"))
    current_utilization = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, verbose_name=_("Current utilization"))

    # Environmental Control Parameters
    min_temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_("Min temperature (°C)"))
    max_temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_("Max temperature (°C)"))
    min_humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_("Min relative humidity (%)"))
    max_humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_("Max relative humidity (%)"))

    # Storage Conditions List
    storage_conditions = models.JSONField(default=list, blank=True, verbose_name=_("Storage conditions"))

    class Meta:
        ordering = ["display_order", "code"]
        verbose_name = "Storage Location"
        verbose_name_plural = "Storage Locations"
        constraints = [
            models.UniqueConstraint(fields=["warehouse", "code"], name="warehouses_storagelocation_wh_code_uniq"),
        ]
        indexes = [
            models.Index(fields=["warehouse", "location_type"]),
            models.Index(fields=["warehouse", "parent"]),
            models.Index(fields=["tenant", "warehouse"]),
        ]

    def __str__(self) -> str:
        return f"{self.warehouse.code} / {self.get_full_path()}"

    @property
    def display_name(self) -> str:
        if self.arabic_name:
            return self.arabic_name
        if self.english_name:
            return self.english_name
        return self.name

    def clean(self) -> None:
        super().clean()
        if self.parent:
            validate_location_hierarchy(self, self.parent)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def get_full_path(self) -> str:
        """Constructs canonical breadcrumb path for location hierarchy."""
        parts = [self.code]
        curr = self.parent
        visited = {self.pk}
        while curr:
            if curr.pk in visited:
                break
            visited.add(curr.pk)
            parts.append(curr.code)
            curr = curr.parent
        return " / ".join(reversed(parts))

    def activate(self) -> None:
        self.status = LocationStatus.ACTIVE
        self.save(update_fields=["status", "updated_at"])

    def deactivate(self) -> None:
        self.status = LocationStatus.INACTIVE
        self.save(update_fields=["status", "updated_at"])

    def restore(self) -> None:
        if self.is_deleted:
            self.is_deleted = False
            self.deleted_at = None
        self.status = LocationStatus.ACTIVE
        self.save(update_fields=["status", "is_deleted", "deleted_at", "updated_at"])
