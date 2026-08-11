"""URL routing for Enterprise Alerts & Recalls API."""

from rest_framework.routers import DefaultRouter

from apps.alerts.api.views import BatchRecallViewSet, InventoryAlertViewSet

router = DefaultRouter()
router.register("alerts", InventoryAlertViewSet, basename="inventory-alert")
router.register("recalls", BatchRecallViewSet, basename="batch-recall")

urlpatterns = router.urls
