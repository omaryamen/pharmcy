"""URL Routing Configuration for Enterprise Reports & BI REST API."""

from rest_framework.routers import DefaultRouter

from apps.reports.api.views import (
    ExecutiveDashboardViewSet,
    FinancialReportViewSet,
    InventoryReportViewSet,
    ReportExportViewSet,
    ReportReconciliationViewSet,
    SalesReportViewSet,
)

router = DefaultRouter()
router.register(r"reports/sales", SalesReportViewSet, basename="reports-sales")
router.register(r"reports/inventory", InventoryReportViewSet, basename="reports-inventory")
router.register(r"reports/financial", FinancialReportViewSet, basename="reports-financial")
router.register(r"reports/dashboard", ExecutiveDashboardViewSet, basename="reports-dashboard")
router.register(r"reports/export", ReportExportViewSet, basename="reports-export")
router.register(r"reports/reconciliation", ReportReconciliationViewSet, basename="reports-reconciliation")

urlpatterns = router.urls
