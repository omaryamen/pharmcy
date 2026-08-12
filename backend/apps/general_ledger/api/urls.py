"""URL Routing Configuration for Enterprise General Ledger REST API."""

from rest_framework.routers import DefaultRouter

from apps.general_ledger.api.views import (
    AccountingPeriodViewSet,
    ChartOfAccountViewSet,
    FinancialReportsViewSet,
    JournalEntryViewSet,
)

router = DefaultRouter()
router.register(r"accounting/accounts", ChartOfAccountViewSet, basename="gl-account")
router.register(r"accounting/journals", JournalEntryViewSet, basename="gl-journal")
router.register(r"accounting/periods", AccountingPeriodViewSet, basename="gl-period")
router.register(r"accounting/reports", FinancialReportsViewSet, basename="gl-reports")

urlpatterns = router.urls
