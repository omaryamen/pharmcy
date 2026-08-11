"""URL route configurations for Stock Transfer API endpoints."""

from rest_framework.routers import DefaultRouter

from apps.stock_transfer.api.views import StockTransferViewSet

router = DefaultRouter()
router.register("stock-transfers", StockTransferViewSet, basename="stock-transfer")

urlpatterns = router.urls
