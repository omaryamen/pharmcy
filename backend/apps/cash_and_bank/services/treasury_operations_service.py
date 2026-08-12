"""TreasuryOperationsService managing Cash Deposits, Cash Withdrawals, and Cash Transfers with GL double-entry integration."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.cash_and_bank.exceptions import InsufficientBankBalanceError, InsufficientCashBalanceError
from apps.cash_and_bank.models import BankAccount, CashAccount, CashDeposit, CashTransfer, CashWithdrawal, OperationStatus
from apps.cash_and_bank.services.number_generator import TreasuryNumberGenerator
from apps.companies.models import Company
from apps.general_ledger.models import ChartOfAccount
from apps.general_ledger.services import JournalPostingService

logger = logging.getLogger(__name__)


class TreasuryOperationsService:
    """Service layer executing Cash Deposits, Cash Withdrawals, and Cash Transfers with double-entry GL journal posting."""

    def __init__(
        self,
        number_generator: TreasuryNumberGenerator | None = None,
        gl_posting_service: JournalPostingService | None = None,
    ) -> None:
        self.number_generator = number_generator or TreasuryNumberGenerator()
        self.gl_posting_service = gl_posting_service or JournalPostingService()

    @transaction.atomic
    def create_cash_deposit(
        self,
        tenant: Any,
        company: Company,
        cash_account: CashAccount,
        bank_account: BankAccount,
        amount: Decimal | float | int,
        *,
        reference: str = "",
        user: Any | None = None,
    ) -> CashDeposit:
        """Deposit physical cash from CashAccount into BankAccount."""
        cash_acc = CashAccount.objects.select_for_update().get(pk=cash_account.pk, tenant=tenant)
        bank_acc = BankAccount.objects.select_for_update().get(pk=bank_account.pk, tenant=tenant)

        dep_amount = Decimal(str(amount))
        if dep_amount <= Decimal("0.0000"):
            raise ValueError("Deposit amount must be greater than zero.")

        if cash_acc.current_balance < dep_amount:
            raise InsufficientCashBalanceError(f"Cash account {cash_acc.name} has insufficient balance (${cash_acc.current_balance}) for deposit of ${dep_amount}.")

        dep_num = self.number_generator.generate_deposit_number(tenant)
        now = timezone.now()

        deposit = CashDeposit.objects.create(
            tenant=tenant,
            company=company,
            cash_account=cash_acc,
            bank_account=bank_acc,
            deposit_number=dep_num,
            deposit_date=now.date(),
            amount=dep_amount,
            reference=reference,
            status=OperationStatus.POSTED,
            approved_by=user,
            posted_at=now,
            created_by=user,
        )

        cash_acc.current_balance -= dep_amount
        cash_acc.save(update_fields=["current_balance", "updated_at"])

        bank_acc.current_balance += dep_amount
        bank_acc.save(update_fields=["current_balance", "updated_at"])

        # Post GL double-entry journal (Debit Bank, Credit Cash)
        bank_gl = bank_acc.gl_account or ChartOfAccount.objects.filter(tenant=tenant, company=company, account_code="1200").first()
        cash_gl = cash_acc.gl_account or ChartOfAccount.objects.filter(tenant=tenant, company=company, account_code="1100").first()

        if bank_gl and cash_gl:
            self.gl_posting_service.create_and_post_journal_entry(
                tenant=tenant,
                company=company,
                posting_date=now.date(),
                description=f"Cash Deposit {dep_num} to {bank_acc.bank_name}",
                lines_data=[
                    {"account": bank_gl, "debit": dep_amount, "credit": Decimal("0.0000"), "description": f"Deposit to {bank_acc.bank_name}"},
                    {"account": cash_gl, "debit": Decimal("0.0000"), "credit": dep_amount, "description": f"Cash drawn from {cash_acc.name}"},
                ],
                reference_type="CASH_DEPOSIT",
                reference_id=str(deposit.pk),
                reference_number=dep_num,
                source_module="cash_and_bank",
                idempotency_key=f"GL-DEP-{deposit.pk}",
                user=user,
            )

        logger.info(f"Posted CashDeposit {dep_num} (${dep_amount}) from {cash_acc.name} to {bank_acc.bank_name}")
        return deposit

    @transaction.atomic
    def create_cash_withdrawal(
        self,
        tenant: Any,
        company: Company,
        bank_account: BankAccount,
        cash_account: CashAccount,
        amount: Decimal | float | int,
        *,
        purpose: str = "",
        reference: str = "",
        user: Any | None = None,
    ) -> CashWithdrawal:
        """Withdraw cash from BankAccount into CashAccount."""
        bank_acc = BankAccount.objects.select_for_update().get(pk=bank_account.pk, tenant=tenant)
        cash_acc = CashAccount.objects.select_for_update().get(pk=cash_account.pk, tenant=tenant)

        wth_amount = Decimal(str(amount))
        if wth_amount <= Decimal("0.0000"):
            raise ValueError("Withdrawal amount must be greater than zero.")

        if bank_acc.current_balance < wth_amount:
            raise InsufficientBankBalanceError(f"Bank account {bank_acc.bank_name} has insufficient balance (${bank_acc.current_balance}) for withdrawal of ${wth_amount}.")

        wth_num = self.number_generator.generate_withdrawal_number(tenant)
        now = timezone.now()

        withdrawal = CashWithdrawal.objects.create(
            tenant=tenant,
            company=company,
            bank_account=bank_acc,
            cash_account=cash_acc,
            withdrawal_number=wth_num,
            withdrawal_date=now.date(),
            amount=wth_amount,
            purpose=purpose,
            reference=reference,
            status=OperationStatus.POSTED,
            approved_by=user,
            posted_at=now,
            created_by=user,
        )

        bank_acc.current_balance -= wth_amount
        bank_acc.save(update_fields=["current_balance", "updated_at"])

        cash_acc.current_balance += wth_amount
        cash_acc.save(update_fields=["current_balance", "updated_at"])

        # Post GL double-entry journal (Debit Cash, Credit Bank)
        cash_gl = cash_acc.gl_account or ChartOfAccount.objects.filter(tenant=tenant, company=company, account_code="1100").first()
        bank_gl = bank_acc.gl_account or ChartOfAccount.objects.filter(tenant=tenant, company=company, account_code="1200").first()

        if cash_gl and bank_gl:
            self.gl_posting_service.create_and_post_journal_entry(
                tenant=tenant,
                company=company,
                posting_date=now.date(),
                description=f"Cash Withdrawal {wth_num} from {bank_acc.bank_name}",
                lines_data=[
                    {"account": cash_gl, "debit": wth_amount, "credit": Decimal("0.0000"), "description": f"Cash deposited to {cash_acc.name}"},
                    {"account": bank_gl, "debit": Decimal("0.0000"), "credit": wth_amount, "description": f"Withdrawal from {bank_acc.bank_name}"},
                ],
                reference_type="CASH_WITHDRAWAL",
                reference_id=str(withdrawal.pk),
                reference_number=wth_num,
                source_module="cash_and_bank",
                idempotency_key=f"GL-WTH-{withdrawal.pk}",
                user=user,
            )

        logger.info(f"Posted CashWithdrawal {wth_num} (${wth_amount}) from {bank_acc.bank_name} to {cash_acc.name}")
        return withdrawal
