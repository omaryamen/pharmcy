"""URL Routing Configuration for Enterprise Customer Sales Returns & Refund Management REST API."""

from rest_framework.routers import DefaultRouter

from apps.sales_returns.api.views import CustomerRefundViewSet, CustomerReturnViewSet

router = DefaultRouter()
router.register(r"customer-returns", CustomerReturnViewSet, basename="customer-return")
router.register(r"customer-refunds", CustomerRefundViewSet, basename="customer-refund")

urlpatterns = router.urls
