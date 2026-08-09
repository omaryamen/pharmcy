"""Warehouse API Views package."""

from apps.warehouses.api.views.location import StorageLocationViewSet
from apps.warehouses.api.views.warehouse import WarehouseViewSet

__all__ = [
    "WarehouseViewSet",
    "StorageLocationViewSet",
]
