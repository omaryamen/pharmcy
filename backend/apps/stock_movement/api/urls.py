"""URL routing for Enterprise Stock Movement Engine."""

from rest_framework.routers import DefaultRouter

from apps.stock_movement.api.views import StockMovementViewSet

router = DefaultRouter()
router.register(r"stock-movements", StockMovementViewSet, basename="stock-movement")

urlpatterns = router.urls
