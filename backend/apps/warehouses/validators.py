"""Validators for Enterprise Warehouse & Storage Location Management."""

from __future__ import annotations

from apps.warehouses.exceptions import (
    CircularLocationHierarchyError,
    InvalidLocationWarehouseMismatchError,
    InvalidWarehouseManagerError,
)


def validate_warehouse_manager(manager, tenant, company) -> None:
    if manager is None:
        return
    if not getattr(manager, "is_active", True):
        raise InvalidWarehouseManagerError("Warehouse manager user account must be active.")
    if hasattr(manager, "tenants") and not manager.tenants.filter(pk=tenant.pk).exists() and not manager.is_superuser:
        raise InvalidWarehouseManagerError("Warehouse manager must belong to the active tenant.")


def validate_location_hierarchy(location, parent) -> None:
    if parent is None:
        return

    # Check warehouse match
    if location.warehouse_id and parent.warehouse_id and location.warehouse_id != parent.warehouse_id:
        raise InvalidLocationWarehouseMismatchError()

    # Check self parentage
    if location.pk and parent.pk == location.pk:
        raise CircularLocationHierarchyError("Storage location cannot be its own parent.")

    # Check circular ancestor chain
    curr = parent
    visited = set()
    if location.pk:
        visited.add(location.pk)

    while curr:
        if curr.pk in visited:
            raise CircularLocationHierarchyError("Circular parent-child relationship detected in location hierarchy.")
        visited.add(curr.pk)
        curr = curr.parent
