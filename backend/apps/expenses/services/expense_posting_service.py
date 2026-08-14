"""ExpensePostingService executing accounting GL double-entry postings, Cash/Bank settlements, and AP integrations."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.accounts_payable.models import AccountsPayableEntry
from apps.cash_and_bank.models import BankAccount, CashAccount
from apps.expenses.exceptions import ExpenseAlreadyPostedError, InvalidExpenseStatusError
from apps.expenses.models import Expense, ExpenseStatus, PaymentMethod
from apps.general_ledger.models import ChartOfAccount
from apps.general_ledger.services import JournalPostingService

logger = logging.getLogger(__name__)


class ExpensePostingService:
    """Service layer executing GL double-entry posting and multi-channel financial settlements for expenses."""

    def __init__(self, gl_posting_service: JournalPostingService | None = None) -> None:
        self.gl_posting_service = gl_posting_service or JournalPostingService()

    @transaction.atomic
    def post_expense(
        self,
        tenant: Any,
        expense: Expense,
        *,
        cash_account: CashAccount | None = None,
        bank_account: BankAccount | None = None,
        user: Any | None = None,
    ) -> Expense:
        """Post approved expense to the General Ledger and execute appropriate settlement integrations."""
        exp = Expense.objects.select_for_update().get(pk=expense.pk, tenant=tenant)

        if exp.accounting_status == "posted":
            raise ExpenseAlreadyPostedError(f"Expense {exp.expense_number} has already been posted.")

        if exp.approval_status != ExpenseStatus.APPROVED:
            raise InvalidExpenseStatusError(f"Expense {exp.expense_number} must be APPROVED prior to posting.")

        company = exp.company
        now = timezone.now()

        # Determine Expense Debit GL Account
        expense_gl = exp.category.gl_expense_account or ChartOfAccount.objects.filter(
            tenant=tenant, company=company, account_code="6000"
        ).first()

        if not expense_gl:
            raise ValueError(f"No GL Expense Account configured for category {exp.category.name} or default 6000.")

        # Determine Settlement Credit GL Account
        credit_gl = None

        if exp.payment_method == PaymentMethod.CASH:
            if cash_account:
                cash_acc = CashAccount.objects.select_for_update().get(pk=cash_account.pk, tenant=tenant)
                cash_acc.current_balance -= exp.total_amount
                cash_acc.save(update_fields=["current_balance", "updated_at"])
                credit_gl = cash_acc.gl_account

            if not credit_gl:
                credit_gl = ChartOfAccount.objects.filter(tenant=tenant, company=company, account_code="1100").first()

            exp.payment_status = "paid"

        elif exp.payment_method == PaymentMethod.BANK:
            if bank_account:
                bank_acc = BankAccount.objects.select_for_update().get(pk=bank_account.pk, tenant=tenant)
                bank_acc.current_balance -= exp.total_amount
                bank_acc.save(update_fields=["current_balance", "updated_at"])
                credit_gl = bank_acc.gl_account

            if not credit_gl:
                credit_gl = ChartOfAccount.objects.filter(tenant=tenant, company=company, account_code="1200").first()

            exp.payment_status = "paid"

        elif exp.payment_method == PaymentMethod.SUPPLIER_PAYABLE:
            credit_gl = ChartOfAccount.objects.filter(tenant=tenant, company=company, account_code="2100").first()
            if exp.supplier:
                from apps.accounts_payable.services import AccountsPayableService
                ap_service = AccountsPayableService()
                inv = ap_service.create_supplier_invoice(
                    tenant=tenant,
                    company=company,
                    supplier=exp.supplier,
                    supplier_invoice_number=exp.expense_number,
                    invoice_date=exp.expense_date,
                    lines_data=[{
                        "description": exp.description or f"Expense {exp.category.name}",
                        "quantity": Decimal("1.0000"),
                        "unit_price": exp.total_amount,
                    }],
                    branch=exp.branch,
                    currency=exp.currency,
                    user=exp.created_by,
                )
                # Approve and post invoice using system/superuser privilege if creator == approver
                inv.status = "approved"
                inv.approved_by = user
                inv.save(update_fields=["status", "approved_by", "updated_at"])
                ap_service.post_supplier_invoice(tenant, inv, user=user)

        elif exp.payment_method == PaymentMethod.EMPLOYEE_REIMBURSEMENT:
            credit_gl = ChartOfAccount.objects.filter(tenant=tenant, company=company, account_code="2000").first()
            if not credit_gl:
                credit_gl = ChartOfAccount.objects.filter(tenant=tenant, company=company, account_code="2100").first()

        if not credit_gl:
            raise ValueError(f"No suitable credit GL account resolved for payment method '{exp.payment_method}'.")

        # Post GL double-entry journal (Debit Expense, Credit Cash/Bank/AP/Liability)
        journal = self.gl_posting_service.create_and_post_journal_entry(
            tenant=tenant,
            company=company,
            posting_date=exp.expense_date,
            description=f"Expense {exp.expense_number}: {exp.description}",
            lines_data=[
                {"account": expense_gl, "debit": exp.total_amount, "credit": Decimal("0.0000"), "description": f"Expense {exp.category.name}"},
                {"account": credit_gl, "debit": Decimal("0.0000"), "credit": exp.total_amount, "description": f"Settlement via {exp.payment_method}"},
            ],
            reference_type="EXPENSE",
            reference_id=str(exp.pk),
            reference_number=exp.expense_number,
            source_module="expenses",
            idempotency_key=f"GL-EXP-{exp.pk}",
            user=user,
        )

        exp.accounting_status = "posted"
        exp.posted_by = user
        exp.posted_at = now
        exp.save()

        logger.info(f"Posted Expense {exp.expense_number} (${exp.total_amount}) to GL Journal {journal.journal_number}")
        return exp
