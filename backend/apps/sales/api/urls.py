"""URL routing for Enterprise POS & Sales Management API."""

from rest_framework.routers import DefaultRouter

from apps.sales.api.views import (
    CashRegisterViewSet,
    RegisterSessionViewSet,
    SalesInvoiceViewSet,
)

router = DefaultRouter()
router.register("sales", SalesInvoiceViewSet, basename="sales-invoice")
router.register("cash-registers", CashRegisterViewSet, basename="cash-register")
router.register("register-sessions", RegisterSessionViewSet, basename="register-session")

urlpatterns = router.urls
