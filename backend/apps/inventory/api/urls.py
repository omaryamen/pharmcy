"""API URL routing configuration for Enterprise Inventory Management module."""

from __future__ import annotations

from rest_framework.routers import DefaultRouter

from apps.inventory.api.views import InventoryItemViewSet

app_name = "inventory"

router = DefaultRouter()
router.register(r"", InventoryItemViewSet, basename="inventory-item")

urlpatterns = router.urls
