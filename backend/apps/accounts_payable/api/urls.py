"""URL routing for Enterprise Supplier Invoices & Accounts Payable Foundation API."""

from rest_framework.routers import DefaultRouter

from apps.accounts_payable.api.views import (
    AccountsPayableViewSet,
    SupplierInvoiceViewSet,
    SupplierPaymentViewSet,
)

router = DefaultRouter()
router.register("supplier-invoices", SupplierInvoiceViewSet, basename="supplier-invoice")
router.register("supplier-payments", SupplierPaymentViewSet, basename="supplier-payment")
router.register("accounts-payable", AccountsPayableViewSet, basename="accounts-payable")

urlpatterns = router.urls
