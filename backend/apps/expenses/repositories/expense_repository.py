"""Repository layer for Expense, ExpenseCategory, and ExpenseRequest entities."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.expenses.models import Expense, ExpenseCategory, ExpenseRequest


class ExpenseCategoryRepository:
    def get_queryset(self, tenant: Any) -> QuerySet[ExpenseCategory]:
        return ExpenseCategory.objects.filter(tenant=tenant)

    def find_by_id(self, tenant: Any, category_id: str) -> ExpenseCategory | None:
        return self.get_queryset(tenant).filter(pk=category_id).first()


class ExpenseRequestRepository:
    def get_queryset(self, tenant: Any) -> QuerySet[ExpenseRequest]:
        return ExpenseRequest.objects.filter(tenant=tenant)

    def find_by_id(self, tenant: Any, request_id: str) -> ExpenseRequest | None:
        return self.get_queryset(tenant).filter(pk=request_id).first()


class ExpenseRepository:
    def get_queryset(self, tenant: Any) -> QuerySet[Expense]:
        return Expense.objects.filter(tenant=tenant)

    def find_by_id(self, tenant: Any, expense_id: str) -> Expense | None:
        return self.get_queryset(tenant).filter(pk=expense_id).first()
