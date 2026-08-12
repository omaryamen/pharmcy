"""URL Routing Configuration for Enterprise Cash, Bank & Treasury REST API."""

from rest_framework.routers import DefaultRouter

from apps.cash_and_bank.api.views import (
    BankAccountViewSet,
    BankReconciliationViewSet,
    BankTransactionViewSet,
    CashAccountViewSet,
    CashDepositViewSet,
    CashTransferViewSet,
    CashWithdrawalViewSet,
    FinancialReconciliationViewSet,
)

router = DefaultRouter()
router.register(r"cash/accounts", CashAccountViewSet, basename="cash-account")
router.register(r"cash/deposits", CashDepositViewSet, basename="cash-deposit")
router.register(r"cash/withdrawals", CashWithdrawalViewSet, basename="cash-withdrawal")
router.register(r"cash/transfers", CashTransferViewSet, basename="cash-transfer")
router.register(r"banks/accounts", BankAccountViewSet, basename="bank-account")
router.register(r"banks/transactions", BankTransactionViewSet, basename="bank-transaction")
router.register(r"banks/reconciliations", BankReconciliationViewSet, basename="bank-reconciliation")
router.register(r"financial-reconciliation", FinancialReconciliationViewSet, basename="financial-reconciliation")

urlpatterns = router.urls
