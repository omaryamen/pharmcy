"""RecurringExpenseService managing recurring expense schedules and duplicate-safe generation."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.utils import timezone

from apps.expenses.models import Expense, ExpenseStatus, PaymentMethod, RecurringExpense, RecurringFrequency
from apps.expenses.services.number_generator import ExpenseNumberGenerator

logger = logging.getLogger(__name__)


class RecurringExpenseService:
    """Service layer automating generation of scheduled recurring operational expenses."""

    def __init__(self, number_generator: ExpenseNumberGenerator | None = None) -> None:
        self.number_generator = number_generator or ExpenseNumberGenerator()

    @transaction.atomic
    def generate_due_recurring_expenses(self, tenant: Any, *, today_date: Any = None) -> list[Expense]:
        """Scan active recurring expense schedules and generate expense records for due items."""
        today = today_date or timezone.now().date()
        schedules = RecurringExpense.objects.select_for_update().filter(
            tenant=tenant, status="active", next_due_date__lte=today
        )

        generated_expenses = []

        for schedule in schedules:
            # Check duplicate protection for the same due date
            existing = Expense.objects.filter(
                tenant=tenant, company=schedule.company, category=schedule.category,
                expense_date=schedule.next_due_date, description__icontains=schedule.name
            ).first()

            if existing:
                logger.info(f"Skipping duplicate recurring expense generation for '{schedule.name}' on {schedule.next_due_date}")
                self._advance_due_date(schedule)
                continue

            exp_num = self.number_generator.generate_expense_number(tenant)
            exp = Expense.objects.create(
                tenant=tenant,
                company=schedule.company,
                branch=schedule.branch,
                category=schedule.category,
                expense_number=exp_num,
                expense_date=schedule.next_due_date,
                description=f"Recurring Expense: {schedule.name}",
                subtotal=schedule.amount,
                total_amount=schedule.amount,
                base_total_amount=schedule.amount,
                currency=schedule.currency,
                payment_method=PaymentMethod.CASH,
                approval_status=ExpenseStatus.APPROVED if schedule.auto_post else ExpenseStatus.SUBMITTED,
                accounting_status="draft",
            )
            generated_expenses.append(exp)

            self._advance_due_date(schedule)

        logger.info(f"Generated {len(generated_expenses)} recurring expenses for tenant {tenant}")
        return generated_expenses

    def _advance_due_date(self, schedule: RecurringExpense) -> None:
        freq = schedule.frequency
        curr = schedule.next_due_date

        if freq == RecurringFrequency.DAILY:
            nxt = curr + relativedelta(days=1)
        elif freq == RecurringFrequency.WEEKLY:
            nxt = curr + relativedelta(weeks=1)
        elif freq == RecurringFrequency.MONTHLY:
            nxt = curr + relativedelta(months=1)
        elif freq == RecurringFrequency.QUARTERLY:
            nxt = curr + relativedelta(months=3)
        elif freq == RecurringFrequency.SEMI_ANNUAL:
            nxt = curr + relativedelta(months=6)
        elif freq == RecurringFrequency.YEARLY:
            nxt = curr + relativedelta(years=1)
        else:
            nxt = curr + relativedelta(months=1)

        schedule.next_due_date = nxt
        if schedule.end_date and nxt > schedule.end_date:
            schedule.status = "completed"
        schedule.save()
