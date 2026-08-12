"""ExpenseSelector layer for expense reports, category analysis, and budget utilization."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db.models import QuerySet, Sum

from apps.expenses.models import Expense, ExpenseBudget, ExpenseCategory, ExpenseStatus


class ExpenseSelector:
    """Selector serving Expense Management reporting, analytics, and budget tracking."""

    def list_expenses(
        self,
        tenant: Any,
        *,
        company_id: str | None = None,
        branch_id: str | None = None,
        category_id: str | None = None,
        approval_status: str | None = None,
        payment_status: str | None = None,
        start_date: Any = None,
        end_date: Any = None,
    ) -> QuerySet[Expense]:
        qs = Expense.objects.filter(tenant=tenant).select_related("company", "branch", "category", "employee", "supplier")
        if company_id:
            qs = qs.filter(company_id=company_id)
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        if category_id:
            qs = qs.filter(category_id=category_id)
        if approval_status:
            qs = qs.filter(approval_status=approval_status)
        if payment_status:
            qs = qs.filter(payment_status=payment_status)
        if start_date:
            qs = qs.filter(expense_date__gte=start_date)
        if end_date:
            qs = qs.filter(expense_date__lte=end_date)
        return qs

    def get_expense_summary(self, tenant: Any, *, company_id: str | None = None) -> dict[str, Any]:
        """Compute aggregated expense metrics for executive reporting."""
        qs = self.list_expenses(tenant, company_id=company_id)
        total_posted = qs.filter(accounting_status="posted").aggregate(val=Sum("total_amount"))["val"] or Decimal("0.0000")
        total_pending = qs.filter(approval_status=ExpenseStatus.PENDING_APPROVAL).aggregate(val=Sum("total_amount"))["val"] or Decimal("0.0000")
        total_unpaid = qs.filter(payment_status="unpaid").aggregate(val=Sum("total_amount"))["val"] or Decimal("0.0000")

        return {
            "total_posted_expenses": total_posted,
            "total_pending_approval": total_pending,
            "total_unpaid_expenses": total_unpaid,
            "total_expense_records_count": qs.count(),
        }
