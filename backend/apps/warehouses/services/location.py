"""Storage Location service managing hierarchical location structure, moves, and lifecycle."""

from __future__ import annotations

import logging
from typing import Any

from django.db import transaction

from apps.warehouses.exceptions import (
    DuplicateLocationCodeError,
    StorageLocationDeleteForbiddenError,
    StorageLocationNotFoundError,
)
from apps.warehouses.models import LocationStatus, StorageLocation, Warehouse
from apps.warehouses.repositories import StorageLocationRepository
from apps.warehouses.validators import validate_location_hierarchy

logger = logging.getLogger(__name__)


class StorageLocationService:
    def __init__(self) -> None:
        self.repository = StorageLocationRepository()

    @transaction.atomic
    def create_location(
        self,
        tenant,
        warehouse: Warehouse,
        *,
        code: str,
        name: str,
        parent: StorageLocation | None = None,
        arabic_name: str = "",
        english_name: str = "",
        description: str = "",
        location_type: str = "zone",
        status: str = "active",
        display_order: int = 0,
        capacity=0.00,
        capacity_unit: str = "units",
        current_utilization=0.00,
        min_temperature=None,
        max_temperature=None,
        min_humidity=None,
        max_humidity=None,
        storage_conditions: list[str] | None = None,
        **extra_fields,
    ) -> StorageLocation:
        clean_code = code.upper().strip()
        clean_name = name.strip()

        if self.repository.exists(warehouse=warehouse, code=clean_code):
            raise DuplicateLocationCodeError(f"Storage location with code '{clean_code}' already exists in warehouse {warehouse.code}.")

        location = StorageLocation(
            tenant=tenant,
            warehouse=warehouse,
            parent=parent,
            code=clean_code,
            name=clean_name,
            arabic_name=arabic_name,
            english_name=english_name,
            description=description,
            location_type=location_type,
            status=status,
            display_order=display_order,
            capacity=capacity,
            capacity_unit=capacity_unit,
            current_utilization=current_utilization,
            min_temperature=min_temperature,
            max_temperature=max_temperature,
            min_humidity=min_humidity,
            max_humidity=max_humidity,
            storage_conditions=storage_conditions or [],
            **extra_fields,
        )

        validate_location_hierarchy(location, parent)
        location.save()

        logger.info("Created storage location %s in warehouse %s", location.get_full_path(), warehouse.code)
        return location

    @transaction.atomic
    def update_location(self, location: StorageLocation, **fields) -> StorageLocation:
        if "parent" in fields:
            validate_location_hierarchy(location, fields["parent"])

        updated = self.repository.update(location, **fields)
        logger.info("Updated storage location %s", location.code)
        return updated

    @transaction.atomic
    def move_location(self, location: StorageLocation, new_parent: StorageLocation | None) -> StorageLocation:
        validate_location_hierarchy(location, new_parent)
        location.parent = new_parent
        location.save(update_fields=["parent", "updated_at"])
        logger.info("Moved location %s to parent %s", location.code, getattr(new_parent, "code", "root"))
        return location

    @transaction.atomic
    def activate_location(self, location: StorageLocation) -> StorageLocation:
        location.activate()
        logger.info("Activated storage location %s", location.code)
        return location

    @transaction.atomic
    def deactivate_location(self, location: StorageLocation) -> StorageLocation:
        location.deactivate()
        logger.info("Deactivated storage location %s", location.code)
        return location

    @transaction.atomic
    def soft_delete_location(self, location: StorageLocation) -> StorageLocation:
        has_children = location.children.filter(is_deleted=False).exists()
        if has_children:
            raise StorageLocationDeleteForbiddenError("Cannot delete storage location containing active child locations.")

        self.repository.delete(location)
        logger.info("Soft deleted storage location %s", location.code)
        return location
