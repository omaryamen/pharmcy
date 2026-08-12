"""ExpenseReversalService executing immutable expense reversals and compensating GL entries."""

from __future__ import annotations

import logging
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.expenses.models import Expense, ExpenseReversal, ExpenseStatus
from apps.expenses.services.number_generator import ExpenseNumberGenerator
from apps.general_ledger.models import JournalEntry
from apps.general_ledger.services import JournalReversalService

logger = logging.getLogger(__name__)


class ExpenseReversalService:
    """Service layer executing immutable expense reversals via compensating GL journals."""

    def __init__(
        self,
        number_generator: ExpenseNumberGenerator | None = None,
        gl_reversal_service: JournalReversalService | None = None,
    ) -> None:
        self.number_generator = number_generator or ExpenseNumberGenerator()
        self.gl_reversal_service = gl_reversal_service or JournalReversalService()

    @transaction.atomic
    def reverse_expense(
        self,
        tenant: Any,
        expense: Expense,
        reason: str,
        *,
        user: Any | None = None,
    ) -> ExpenseReversal:
        """Reverse a posted expense immutably by posting a compensating GL journal."""
        exp = Expense.objects.select_for_update().get(pk=expense.pk, tenant=tenant)

        rev_num = self.number_generator.generate_reversal_number(tenant)
        now = timezone.now()

        reversal = ExpenseReversal.objects.create(
            tenant=tenant,
            expense=exp,
            reversal_number=rev_num,
            reversal_date=now.date(),
            reason=reason,
            approved_by=user,
            created_by=user,
        )

        # Reverse posted GL journal if present
        orig_journal = JournalEntry.objects.filter(tenant=tenant, reference_id=str(exp.pk), source_module="expenses").first()
        if orig_journal:
            self.gl_reversal_service.reverse_journal_entry(
                tenant=tenant,
                journal_entry=orig_journal,
                reversal_reason=f"Reversal of Expense {exp.expense_number}: {reason}",
                user=user,
            )

        exp.approval_status = ExpenseStatus.REVERSED
        exp.save(update_fields=["approval_status", "updated_at"])

        logger.info(f"Reversed Expense {exp.expense_number} via Reversal {rev_num}")
        return reversal
