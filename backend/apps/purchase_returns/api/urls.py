"""URL routing for Enterprise Purchase Returns & Supplier Returns API."""

from rest_framework.routers import DefaultRouter

from apps.purchase_returns.api.views import PurchaseReturnViewSet

router = DefaultRouter()
router.register("purchase-returns", PurchaseReturnViewSet, basename="purchase-return")

urlpatterns = router.urls
