"""URL Routing Configuration for Enterprise Expenses REST API."""

from rest_framework.routers import DefaultRouter

from apps.expenses.api.views import (
    EmployeeExpenseViewSet,
    ExpenseBudgetViewSet,
    ExpenseCategoryViewSet,
    ExpenseRequestViewSet,
    ExpenseStatisticsViewSet,
    ExpenseViewSet,
)

router = DefaultRouter()
router.register(r"expense-categories", ExpenseCategoryViewSet, basename="expense-category")
router.register(r"expense-requests", ExpenseRequestViewSet, basename="expense-request")
router.register(r"expenses", ExpenseViewSet, basename="expense")
router.register(r"employee-expenses", EmployeeExpenseViewSet, basename="employee-expense")
router.register(r"expense-budgets", ExpenseBudgetViewSet, basename="expense-budget")
router.register(r"expense-analytics", ExpenseStatisticsViewSet, basename="expense-analytics")

urlpatterns = router.urls
