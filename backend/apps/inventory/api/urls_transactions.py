"""API URL routing configuration for standalone Inventory Transaction endpoints."""

from __future__ import annotations

from rest_framework.routers import DefaultRouter

from apps.inventory.api.views import InventoryTransactionViewSet

app_name = "inventory-transactions"

router = DefaultRouter()
router.register(r"", InventoryTransactionViewSet, basename="inventory-transaction")

urlpatterns = router.urls
