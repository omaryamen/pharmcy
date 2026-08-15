"""URL Routing Configuration for Commerce REST API."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.commerce.api.views import (
    CartViewSet,
    CheckoutViewSet,
    CommerceOrderViewSet,
    CommercePaymentViewSet,
    OrderPrescriptionViewSet,
    StoreProductViewSet,
    TenantStoreViewSet,
)

router = DefaultRouter()
router.register(r"store/stores", TenantStoreViewSet, basename="store-stores")
router.register(r"store/products", StoreProductViewSet, basename="store-products")
router.register(r"store/cart", CartViewSet, basename="store-cart")
router.register(r"store/orders", CommerceOrderViewSet, basename="store-orders")
router.register(r"store/prescriptions", OrderPrescriptionViewSet, basename="store-prescriptions")
router.register(r"store/payments", CommercePaymentViewSet, basename="store-payments")

urlpatterns = router.urls + [
    path("store/checkout/", CheckoutViewSet.as_view(), name="store-checkout"),
]
