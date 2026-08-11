"""URL routing for Enterprise Purchasing & Purchase Order API."""

from rest_framework.routers import DefaultRouter

from apps.procurement.api.views import (
    PurchaseOrderViewSet,
    PurchaseRequisitionViewSet,
    SupplierProductPriceViewSet,
)

router = DefaultRouter()
router.register("purchase-requisitions", PurchaseRequisitionViewSet, basename="purchase-requisition")
router.register("purchase-orders", PurchaseOrderViewSet, basename="purchase-order")
router.register("supplier-prices", SupplierProductPriceViewSet, basename="supplier-price")

urlpatterns = router.urls
