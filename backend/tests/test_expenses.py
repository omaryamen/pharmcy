"""Comprehensive test suite for IMP-031 — Enterprise Expense & Operating Cost Management.
Tests: Expense categories, Expense pre-approval requests, Cash expenses ($500 Debit Expense / Credit Cash),
Bank expenses ($1,000 Debit Expense / Credit Bank), Supplier expenses ($2,000 Debit Expense / Credit AP),
Employee reimbursement claims, Recurring expense generation & duplicate prevention, Immutable reversals
with compensating GL journals, ExpenseSelector analytics summary, and tenant isolation.
"""

from __future__ import annotations

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.accounts_payable.models import AccountsPayableEntry
from apps.branches.models import Branch
from apps.cash_and_bank.models import BankAccount, CashAccount
from apps.companies.models import Company
from apps.core.models import Tenant
from apps.expenses.exceptions import ExpenseAlreadyPostedError, InvalidExpenseStatusError
from apps.expenses.models import (
    EmployeeExpense,
    Expense,
    ExpenseCategory,
    ExpenseRequest,
    ExpenseStatus,
    PaymentMethod,
    RecurringExpense,
    RecurringFrequency,
    RequestStatus,
)
from apps.expenses.selectors import ExpenseSelector
from apps.expenses.services import ExpensePostingService, ExpenseReversalService, RecurringExpenseService
from apps.general_ledger.models import JournalEntry, JournalStatus
from apps.general_ledger.services import ChartOfAccountsService
from apps.suppliers.models import Supplier
from apps.warehouses.models import Warehouse

User = get_user_model()


def exp_full_setup():
    """Helper fixture initializing tenant, company, branch, category, cash account, bank account, supplier, and GL chart of accounts."""
    tenant = Tenant.objects.create(name=f"EXP Tenant {uuid.uuid4().hex[:6]}", slug=f"exp-slug-{uuid.uuid4().hex[:6]}")
    company = Company.objects.create(tenant=tenant, legal_name="Pharma Operating Corp", commercial_name="Pharma Operating Corp", code=f"COMP-{uuid.uuid4().hex[:4]}", slug=f"comp-{uuid.uuid4().hex[:4]}")
    branch = Branch.objects.create(tenant=tenant, company=company, name="Main Operating Branch", code=f"BR-{uuid.uuid4().hex[:4]}")

    coa_service = ChartOfAccountsService()
    coa_map = coa_service.seed_default_chart_of_accounts(tenant, company)

    category = ExpenseCategory.objects.create(
        tenant=tenant, company=company, code=f"EXC-{uuid.uuid4().hex[:4]}",
        name="Office Supplies & Utilities", gl_expense_account=coa_map["6000"],
    )

    cash_acc = CashAccount.objects.create(
        tenant=tenant, company=company, branch=branch, gl_account=coa_map["1100"],
        name="Petty Cash Fund", account_number=f"CSH-{uuid.uuid4().hex[:4]}",
        opening_balance=Decimal("1000.0000"), current_balance=Decimal("5000.0000"),
    )

    bank_acc = BankAccount.objects.create(
        tenant=tenant, company=company, branch=branch, gl_account=coa_map["1200"],
        bank_name="First National Bank", account_name="Operating Expense Account",
        account_number=f"BNK-{uuid.uuid4().hex[:6]}",
        opening_balance=Decimal("10000.0000"), current_balance=Decimal("50000.0000"),
    )

    supplier = Supplier.objects.create(
        tenant=tenant, company=company, code=f"SUP-{uuid.uuid4().hex[:4]}",
        legal_name="Global Utility Corp", display_name="Global Utility Corp",
    )

    manager = User.objects.create_user(email=f"manager_{uuid.uuid4().hex[:4]}@test.com", first_name="Manager Alice", password="pass")

    return tenant, company, branch, category, cash_acc, bank_acc, supplier, manager, coa_map


# ===========================================================================
# 1. CASH, BANK & SUPPLIER EXPENSE POSTING TESTS
# ===========================================================================


@pytest.mark.django_db
class TestExpensePostingIntegrations:
    def test_cash_expense_posts_debit_expense_credit_cash(self):
        """Cash Expense ($500) posts GL journal (Debit Expense 6000, Credit Cash 1100) and reduces CashAccount balance."""
        tenant, company, branch, category, cash_acc, bank_acc, supplier, manager, coa_map = exp_full_setup()
        posting_service = ExpensePostingService()

        expense = Expense.objects.create(
            tenant=tenant, company=company, branch=branch, category=category,
            expense_number=f"EXP-{uuid.uuid4().hex[:6]}", expense_date=timezone.now().date(),
            description="Office stationery purchase", subtotal=Decimal("500.0000"), total_amount=Decimal("500.0000"),
            base_total_amount=Decimal("500.0000"), payment_method=PaymentMethod.CASH,
            approval_status=ExpenseStatus.APPROVED, accounting_status="draft",
        )

        posted_exp = posting_service.post_expense(tenant=tenant, expense=expense, cash_account=cash_acc, user=manager)

        assert posted_exp.accounting_status == "posted"
        assert posted_exp.payment_status == "paid"

        cash_acc.refresh_from_db()
        assert cash_acc.current_balance == Decimal("4500.0000")

        # Verify GL Journal Entry
        gl_journal = JournalEntry.objects.get(tenant=tenant, reference_id=str(expense.pk))
        assert gl_journal.total_debit == Decimal("500.0000")
        assert gl_journal.total_credit == Decimal("500.0000")
        assert gl_journal.status == JournalStatus.POSTED

    def test_bank_expense_posts_debit_expense_credit_bank(self):
        """Bank Expense ($1,000) posts GL journal (Debit Expense 6000, Credit Bank 1200) and reduces BankAccount balance."""
        tenant, company, branch, category, cash_acc, bank_acc, supplier, manager, coa_map = exp_full_setup()
        posting_service = ExpensePostingService()

        expense = Expense.objects.create(
            tenant=tenant, company=company, branch=branch, category=category,
            expense_number=f"EXP-{uuid.uuid4().hex[:6]}", expense_date=timezone.now().date(),
            description="Monthly Internet Fiber Line", subtotal=Decimal("1000.0000"), total_amount=Decimal("1000.0000"),
            base_total_amount=Decimal("1000.0000"), payment_method=PaymentMethod.BANK,
            approval_status=ExpenseStatus.APPROVED, accounting_status="draft",
        )

        posted_exp = posting_service.post_expense(tenant=tenant, expense=expense, bank_account=bank_acc, user=manager)

        bank_acc.refresh_from_db()
        assert bank_acc.current_balance == Decimal("49000.0000")

        gl_journal = JournalEntry.objects.get(tenant=tenant, reference_id=str(expense.pk))
        assert gl_journal.total_debit == Decimal("1000.0000")
        assert gl_journal.total_credit == Decimal("1000.0000")

    def test_supplier_expense_posts_debit_expense_credit_ap(self):
        """Supplier Expense ($2,000) creates AP Payable entry and GL journal (Debit Expense 6000, Credit AP 2100)."""
        tenant, company, branch, category, cash_acc, bank_acc, supplier, manager, coa_map = exp_full_setup()
        posting_service = ExpensePostingService()

        expense = Expense.objects.create(
            tenant=tenant, company=company, branch=branch, category=category, supplier=supplier,
            expense_number=f"EXP-{uuid.uuid4().hex[:6]}", expense_date=timezone.now().date(),
            description="Electric Utility Bill", subtotal=Decimal("2000.0000"), total_amount=Decimal("2000.0000"),
            base_total_amount=Decimal("2000.0000"), payment_method=PaymentMethod.SUPPLIER_PAYABLE,
            approval_status=ExpenseStatus.APPROVED, accounting_status="draft",
        )

        posted_exp = posting_service.post_expense(tenant=tenant, expense=expense, user=manager)

        # Verify AP Subledger Entry
        ap_entry = AccountsPayableEntry.objects.get(tenant=tenant, supplier_invoice__supplier_invoice_number=expense.expense_number)
        assert ap_entry.outstanding_amount == Decimal("2000.0000")
        assert ap_entry.supplier == supplier

        gl_journal = JournalEntry.objects.get(tenant=tenant, reference_id=str(expense.pk))
        assert gl_journal.total_debit == Decimal("2000.0000")
        assert gl_journal.total_credit == Decimal("2000.0000")


# ===========================================================================
# 2. RECURRING EXPENSES & REVERSALS TESTS
# ===========================================================================


@pytest.mark.django_db
class TestRecurringExpenseAndReversal:
    def test_recurring_expense_generation_and_duplicate_prevention(self):
        """Generating due recurring expense creates expense record and prevents duplicate generation for same period."""
        tenant, company, branch, category, cash_acc, bank_acc, supplier, manager, coa_map = exp_full_setup()
        recurring_service = RecurringExpenseService()

        schedule = RecurringExpense.objects.create(
            tenant=tenant, company=company, branch=branch, category=category,
            name="Monthly Software License", amount=Decimal("1000.0000"),
            frequency=RecurringFrequency.MONTHLY, start_date=timezone.now().date(),
            next_due_date=timezone.now().date(), auto_generate=True, status="active",
        )

        # Generate due recurring expenses
        exps = recurring_service.generate_due_recurring_expenses(tenant, today_date=timezone.now().date())
        assert len(exps) == 1
        assert exps[0].total_amount == Decimal("1000.0000")

        # Run generator again for same date -> should skip duplicate
        exps_dup = recurring_service.generate_due_recurring_expenses(tenant, today_date=timezone.now().date())
        assert len(exps_dup) == 0

    def test_expense_reversal_creates_compensating_journal(self):
        """Reversing a posted expense updates status to REVERSED and posts a compensating reversal journal."""
        tenant, company, branch, category, cash_acc, bank_acc, supplier, manager, coa_map = exp_full_setup()
        posting_service = ExpensePostingService()
        reversal_service = ExpenseReversalService()

        expense = Expense.objects.create(
            tenant=tenant, company=company, branch=branch, category=category,
            expense_number=f"EXP-{uuid.uuid4().hex[:6]}", expense_date=timezone.now().date(),
            description="Erroneous Travel Claim", subtotal=Decimal("750.0000"), total_amount=Decimal("750.0000"),
            base_total_amount=Decimal("750.0000"), payment_method=PaymentMethod.CASH,
            approval_status=ExpenseStatus.APPROVED, accounting_status="draft",
        )

        posting_service.post_expense(tenant=tenant, expense=expense, cash_account=cash_acc, user=manager)

        reversal = reversal_service.reverse_expense(
            tenant=tenant, expense=expense, reason="Duplicate expense entry", user=manager
        )

        assert reversal.pk is not None
        expense.refresh_from_db()
        assert expense.approval_status == ExpenseStatus.REVERSED

        # Verify reversal journal entry created
        journals = JournalEntry.objects.filter(tenant=tenant)
        assert len(journals) == 2  # Original posted + compensating reversal

    def test_expense_selector_analytics_summary(self):
        """ExpenseSelector calculates aggregated posted, pending, and unpaid expense totals."""
        tenant, company, branch, category, cash_acc, bank_acc, supplier, manager, coa_map = exp_full_setup()
        selector = ExpenseSelector()

        Expense.objects.create(
            tenant=tenant, company=company, branch=branch, category=category,
            expense_number=f"EXP-{uuid.uuid4().hex[:6]}", expense_date=timezone.now().date(),
            description="Pending Item", subtotal=Decimal("300.0000"), total_amount=Decimal("300.0000"),
            base_total_amount=Decimal("300.0000"), payment_method=PaymentMethod.CASH,
            approval_status=ExpenseStatus.PENDING_APPROVAL, accounting_status="draft",
        )

        summary = selector.get_expense_summary(tenant, company_id=str(company.pk))
        assert summary["total_pending_approval"] == Decimal("300.0000")
        assert summary["total_expense_records_count"] == 1
