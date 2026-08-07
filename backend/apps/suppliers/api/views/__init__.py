"""Supplier API views."""

from .stats import SupplierStatsView
from .supplier import SupplierViewSet

__all__ = ["SupplierViewSet", "SupplierStatsView"]
