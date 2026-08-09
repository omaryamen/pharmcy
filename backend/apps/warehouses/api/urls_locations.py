"""API URL routing configuration for standalone Storage Location endpoints."""

from __future__ import annotations

from rest_framework.routers import DefaultRouter

from apps.warehouses.api.views import StorageLocationViewSet

app_name = "storage-locations"

router = DefaultRouter()
router.register(r"", StorageLocationViewSet, basename="storage-location")

urlpatterns = router.urls
