"""Domain enumeration choices for Enterprise Warehouse & Storage Location Management."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class WarehouseType(models.TextChoices):
    MAIN = "main", _("Main Warehouse")
    PHARMACY = "pharmacy", _("Pharmacy Warehouse")
    BRANCH = "branch", _("Branch Warehouse")
    DISTRIBUTION_CENTER = "distribution_center", _("Distribution Center")
    COLD_STORAGE = "cold_storage", _("Cold Storage")
    CONTROLLED_DRUG = "controlled_drug", _("Controlled Drug Storage")
    QUARANTINE = "quarantine", _("Quarantine Storage")
    RETURNS = "returns", _("Returns Storage")
    DAMAGED = "damaged", _("Damaged Goods Storage")
    TRANSIT = "transit", _("Transit Storage")
    VIRTUAL = "virtual", _("Virtual Warehouse")
    OTHER = "other", _("Other Storage")


class WarehouseStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    ACTIVE = "active", _("Active")
    INACTIVE = "inactive", _("Inactive")
    SUSPENDED = "suspended", _("Suspended")
    TEMPORARILY_CLOSED = "temporarily_closed", _("Temporarily Closed")
    ARCHIVED = "archived", _("Archived")


class LocationType(models.TextChoices):
    ZONE = "zone", _("Zone")
    AISLE = "aisle", _("Aisle")
    RACK = "rack", _("Rack")
    SHELF = "shelf", _("Shelf")
    BIN = "bin", _("Bin")
    ROOM = "room", _("Room")
    CABINET = "cabinet", _("Cabinet")
    COLD_ROOM = "cold_room", _("Cold Room")
    FREEZER = "freezer", _("Freezer")
    QUARANTINE_AREA = "quarantine_area", _("Quarantine Area")
    RETURNS_AREA = "returns_area", _("Returns Area")
    DAMAGED_AREA = "damaged_area", _("Damaged Area")
    OTHER = "other", _("Other Location")


class LocationStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    INACTIVE = "inactive", _("Inactive")
    MAINTENANCE = "maintenance", _("Under Maintenance")
    BLOCKED = "blocked", _("Blocked")
    FULL = "full", _("Full Capacity")


class StorageCondition(models.TextChoices):
    AMBIENT = "ambient", _("Ambient Temperature (15-25°C)")
    REFRIGERATED = "refrigerated", _("Refrigerated (2-8°C)")
    FROZEN = "frozen", _("Frozen (-20°C)")
    CONTROLLED_TEMP = "controlled_temp", _("Controlled Temperature")
    PROTECTED_LIGHT = "protected_light", _("Protected From Light")
    HUMIDITY_CONTROLLED = "humidity_controlled", _("Humidity Controlled")
    CONTROLLED_ACCESS = "controlled_access", _("Controlled Access / Vault")
    HAZARDOUS = "hazardous", _("Hazardous Storage")
    NARCOTIC = "narcotic", _("Narcotics Cabinet")
    PSYCHOTROPIC = "psychotropic", _("Psychotropics Storage")
    QUARANTINE = "quarantine", _("Quarantine Restricted")
