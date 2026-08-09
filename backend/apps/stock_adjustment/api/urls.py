"""URL routing for Enterprise Stock Adjustment & Stock Count module."""

from rest_framework.routers import DefaultRouter

from apps.stock_adjustment.api.views import StockCountViewSet

router = DefaultRouter()
router.register(r"stock-counts", StockCountViewSet, basename="stock-count")

urlpatterns = router.urls
