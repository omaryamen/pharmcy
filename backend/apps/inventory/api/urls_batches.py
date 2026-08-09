"""API URL routing configuration for standalone Batch endpoints."""

from __future__ import annotations

from rest_framework.routers import DefaultRouter

from apps.inventory.api.views import BatchViewSet

app_name = "batches"

router = DefaultRouter()
router.register(r"", BatchViewSet, basename="batch")

urlpatterns = router.urls
