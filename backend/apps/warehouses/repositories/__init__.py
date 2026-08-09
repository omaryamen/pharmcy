"""Warehouse repositories package."""

from apps.warehouses.repositories.location import StorageLocationRepository
from apps.warehouses.repositories.warehouse import WarehouseRepository

__all__ = [
    "WarehouseRepository",
    "StorageLocationRepository",
]
