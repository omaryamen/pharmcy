"""FinancialReconciliationService orchestrating bank statement matching, discrepancy logging, and reconciliation session approval."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.cash_and_bank.models import (
    BankAccount,
    BankReconciliation,
    BankReconciliationStatus,
    BankTransaction,
    ReconciliationException,
    ReconciliationMatch,
    ReconciliationMatchStatus,
)
from apps.cash_and_bank.services.number_generator import TreasuryNumberGenerator
from apps.companies.models import Company

logger = logging.getLogger(__name__)


class FinancialReconciliationService:
    """Service layer executing bank statement matching, reconciliation exception logging, and audit finalization."""

    def __init__(self, number_generator: TreasuryNumberGenerator | None = None) -> None:
        self.number_generator = number_generator or TreasuryNumberGenerator()

    @transaction.atomic
    def create_reconciliation_session(
        self,
        tenant: Any,
        company: Company,
        bank_account: BankAccount,
        start_date: Any,
        end_date: Any,
        statement_closing_balance: Decimal | float | int,
        *,
        opening_balance: Decimal | float | int = Decimal("0.0000"),
        user: Any | None = None,
    ) -> BankReconciliation:
        """Initialize a new BankReconciliation session."""
        rec_num = self.number_generator.generate_reconciliation_number(tenant)
        stmt_bal = Decimal(str(statement_closing_balance))
        book_bal = bank_account.current_balance
        diff = stmt_bal - book_bal

        reconciliation = BankReconciliation.objects.create(
            tenant=tenant,
            company=company,
            bank_account=bank_account,
            reconciliation_number=rec_num,
            start_date=start_date,
            end_date=end_date,
            opening_balance=Decimal(str(opening_balance)),
            statement_closing_balance=stmt_bal,
            book_closing_balance=book_bal,
            difference=diff,
            status=BankReconciliationStatus.IN_PROGRESS if diff != Decimal("0.0000") else BankReconciliationStatus.RECONCILED,
            created_by=user,
        )

        logger.info(f"Created BankReconciliation {rec_num} for {bank_account.bank_name} (Difference: ${diff})")
        return reconciliation

    @transaction.atomic
    def match_transaction(
        self,
        tenant: Any,
        reconciliation: BankReconciliation,
        bank_transaction: BankTransaction,
        reference_type: str,
        reference_id: str,
        matched_amount: Decimal | float | int,
        *,
        is_auto_matched: bool = False,
    ) -> ReconciliationMatch:
        """Link a BankTransaction to a book entry (e.g. CustomerPayment, SupplierPayment, CashDeposit)."""
        btx = BankTransaction.objects.select_for_update().get(pk=bank_transaction.pk, tenant=tenant)
        amt = Decimal(str(matched_amount))

        match = ReconciliationMatch.objects.create(
            tenant=tenant,
            reconciliation=reconciliation,
            bank_transaction=btx,
            matched_amount=amt,
            reference_type=reference_type,
            reference_id=reference_id,
            is_auto_matched=is_auto_matched,
        )

        btx.reconciliation_status = ReconciliationMatchStatus.MATCHED
        btx.save(update_fields=["reconciliation_status", "updated_at"])

        logger.info(f"Matched BankTransaction {btx.transaction_number} to {reference_type} #{reference_id}")
        return match

    @transaction.atomic
    def approve_reconciliation(
        self,
        tenant: Any,
        reconciliation: BankReconciliation,
        approver: Any,
    ) -> BankReconciliation:
        """Approve and finalize bank reconciliation session."""
        rec = BankReconciliation.objects.select_for_update().get(pk=reconciliation.pk, tenant=tenant)

        rec.status = BankReconciliationStatus.CLOSED if rec.difference == Decimal("0.0000") else BankReconciliationStatus.DISCREPANCY
        rec.approved_by = approver
        rec.reconciled_at = timezone.now()
        rec.save()

        logger.info(f"Finalized BankReconciliation {rec.reconciliation_number} with status '{rec.status}'")
        return rec
