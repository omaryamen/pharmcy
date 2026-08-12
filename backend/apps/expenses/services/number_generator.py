"""Sequence number generator for Expense domain entities."""

from __future__ import annotations

import logging
from typing import Any

from django.utils import timezone

from apps.expenses.models import (
    EmployeeExpense,
    Expense,
    ExpenseAdjustment,
    ExpenseCategory,
    ExpenseRequest,
    ExpenseReversal,
)

logger = logging.getLogger(__name__)


class ExpenseNumberGenerator:
    """Generates unique collision-safe sequence codes for Expense domain models."""

    def _generate_seq(self, tenant: Any, model_cls: Any, field_name: str, prefix_str: str) -> str:
        year = timezone.now().year
        prefix = f"{prefix_str}-{year}-"
        filter_kwargs = {f"{field_name}__startswith": prefix, "tenant": tenant}
        last = model_cls.objects.filter(**filter_kwargs).order_by(f"-{field_name}").first()
        if last:
            val = getattr(last, field_name, "")
            try:
                seq = int(val.rsplit("-", 1)[-1]) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1
        return f"{prefix}{seq:06d}"

    def generate_category_code(self, tenant: Any) -> str:
        return self._generate_seq(tenant, ExpenseCategory, "code", "EXC")

    def generate_request_number(self, tenant: Any) -> str:
        return self._generate_seq(tenant, ExpenseRequest, "request_number", "EXR")

    def generate_expense_number(self, tenant: Any) -> str:
        return self._generate_seq(tenant, Expense, "expense_number", "EXP")

    def generate_claim_number(self, tenant: Any) -> str:
        return self._generate_seq(tenant, EmployeeExpense, "claim_number", "EEX")

    def generate_reversal_number(self, tenant: Any) -> str:
        return self._generate_seq(tenant, ExpenseReversal, "reversal_number", "EXV")

    def generate_adjustment_number(self, tenant: Any) -> str:
        return self._generate_seq(tenant, ExpenseAdjustment, "adjustment_number", "EXA")
