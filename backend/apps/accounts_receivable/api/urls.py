"""URL Routing Configuration for Enterprise Accounts Receivable REST API."""

from rest_framework.routers import DefaultRouter

from apps.accounts_receivable.api.views import (
    ARAnalyticsViewSet,
    CustomerPaymentViewSet,
    CustomerReceivableViewSet,
    CustomerStatementViewSet,
)

router = DefaultRouter()
router.register(r"accounts-receivable", CustomerReceivableViewSet, basename="customer-receivable")
router.register(r"customer-payments", CustomerPaymentViewSet, basename="customer-payment")
router.register(r"customer-statements", CustomerStatementViewSet, basename="customer-statement")
router.register(r"ar-analytics", ARAnalyticsViewSet, basename="ar-analytics")

urlpatterns = router.urls
