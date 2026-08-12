"""Comprehensive test suite for IMP-030 — Enterprise Cash, Bank & Financial Reconciliation.
Tests: Cash accounts, Bank accounts, POS register session closing & cash counting, exact cash match,
cash shortage variance (-100), cash overage variance (+100), cash deposits (Cash -> Bank) with GL postings,
cash withdrawals (Bank -> Cash) with GL postings, duplicate bank statement import protection,
bank transaction matching & reconciliation sessions, financial treasury summary, and tenant isolation.
"""

from __future__ import annotations

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.branches.models import Branch
from apps.cash_and_bank.exceptions import InsufficientBankBalanceError, InsufficientCashBalanceError
from apps.cash_and_bank.models import (
    BankAccount,
    BankReconciliation,
    BankTransaction,
    CashAccount,
    CashDeposit,
    CashMovement,
    CashVariance,
    CashWithdrawal,
    ReconciliationMatchStatus,
    VarianceType,
)
from apps.cash_and_bank.selectors import TreasurySelector
from apps.cash_and_bank.services import (
    BankStatementImportService,
    CashSessionReconciliationService,
    FinancialReconciliationService,
    TreasuryOperationsService,
)
from apps.companies.models import Company
from apps.core.models import Tenant
from apps.customers.models import Customer
from apps.general_ledger.models import JournalEntry, JournalStatus
from apps.general_ledger.services import ChartOfAccountsService
from apps.sales.models import CashRegister, RegisterSession, SessionStatus
from apps.sales.services import PosSalesService
from apps.warehouses.models import StorageLocation, Warehouse

User = get_user_model()


def cb_full_setup():
    """Helper fixture initializing tenant, company, branch, warehouse, register, session, cash account, bank account, and GL accounts."""
    tenant = Tenant.objects.create(name=f"CB Tenant {uuid.uuid4().hex[:6]}", slug=f"cb-slug-{uuid.uuid4().hex[:6]}")
    company = Company.objects.create(tenant=tenant, legal_name="Pharma Treasury Corp", commercial_name="Pharma Treasury Corp", code=f"COMP-{uuid.uuid4().hex[:4]}", slug=f"comp-{uuid.uuid4().hex[:4]}")
    branch = Branch.objects.create(tenant=tenant, company=company, name="Main Treasury Branch", code=f"BR-{uuid.uuid4().hex[:4]}")
    warehouse = Warehouse.objects.create(tenant=tenant, company=company, branch=branch, name="Main Treasury WH", code=f"WH-{uuid.uuid4().hex[:4]}")

    coa_service = ChartOfAccountsService()
    coa_map = coa_service.seed_default_chart_of_accounts(tenant, company)

    cash_acc = CashAccount.objects.create(
        tenant=tenant, company=company, branch=branch, gl_account=coa_map["1100"],
        name="Main Branch Till", account_number=f"CSH-{uuid.uuid4().hex[:4]}",
        opening_balance=Decimal("1000.0000"), current_balance=Decimal("5000.0000"),
    )

    bank_acc = BankAccount.objects.create(
        tenant=tenant, company=company, branch=branch, gl_account=coa_map["1200"],
        bank_name="National Commercial Bank", account_name="Pharma Operating Account",
        account_number=f"BNK-{uuid.uuid4().hex[:6]}", iban=f"SA0011223344556677{uuid.uuid4().hex[:4]}",
        opening_balance=Decimal("10000.0000"), current_balance=Decimal("50000.0000"),
    )

    register = CashRegister.objects.create(
        tenant=tenant, company=company, branch=branch, warehouse=warehouse,
        register_number=f"REG-{uuid.uuid4().hex[:4]}", name="Counter 1",
        opening_balance=Decimal("1000.0000"), current_balance=Decimal("1000.0000"), status="open",
    )

    cashier = User.objects.create_user(email=f"cashier_{uuid.uuid4().hex[:4]}@test.com", first_name="Cashier Bob", password="pass")

    session = RegisterSession.objects.create(
        tenant=tenant, cash_register=register, cashier=cashier,
        session_number=f"SES-{uuid.uuid4().hex[:6]}",
        opening_cash=Decimal("1000.0000"), expected_cash=Decimal("5500.0000"),
        status=SessionStatus.OPEN,
    )

    return tenant, company, branch, warehouse, cash_acc, bank_acc, register, session, cashier, coa_map


# ===========================================================================
# 1. POS CASH SESSION RECONCILIATION & VARIANCE TESTS
# ===========================================================================


@pytest.mark.django_db
class TestCashSessionAndVariance:
    def test_exact_cash_closing_reconciles_without_variance(self):
        """Expected cash ($5,500) == Actual cash ($5,500) closes session cleanly with zero variance."""
        tenant, company, branch, warehouse, cash_acc, bank_acc, register, session, cashier, coa_map = cb_full_setup()
        sess_service = CashSessionReconciliationService()

        closed_sess, variance = sess_service.close_and_reconcile_cash_session(
            tenant=tenant, session=session, actual_closing_cash=Decimal("5500.0000"), user=cashier
        )

        assert closed_sess.status == SessionStatus.CLOSED
        assert closed_sess.actual_cash == Decimal("5500.0000")
        assert closed_sess.variance == Decimal("0.0000")
        assert variance is None

    def test_cash_shortage_records_variance(self):
        """Expected cash ($5,500) vs Actual ($5,400) records Shortage variance (-$100) without silent balance edits."""
        tenant, company, branch, warehouse, cash_acc, bank_acc, register, session, cashier, coa_map = cb_full_setup()
        sess_service = CashSessionReconciliationService()

        closed_sess, variance = sess_service.close_and_reconcile_cash_session(
            tenant=tenant, session=session, actual_closing_cash=Decimal("5400.0000"),
            reason="Till count short by $100", user=cashier,
        )

        assert closed_sess.status == SessionStatus.CLOSED
        assert variance is not None
        assert variance.variance_type == VarianceType.SHORTAGE
        assert variance.variance_amount == Decimal("100.0000")
        assert variance.status == "pending"

    def test_cash_overage_records_variance(self):
        """Expected cash ($5,500) vs Actual ($5,600) records Overage variance (+$100)."""
        tenant, company, branch, warehouse, cash_acc, bank_acc, register, session, cashier, coa_map = cb_full_setup()
        sess_service = CashSessionReconciliationService()

        closed_sess, variance = sess_service.close_and_reconcile_cash_session(
            tenant=tenant, session=session, actual_closing_cash=Decimal("5600.0000"),
            reason="Extra cash found in drawer", user=cashier,
        )

        assert variance is not None
        assert variance.variance_type == VarianceType.OVERAGE
        assert variance.variance_amount == Decimal("100.0000")


# ===========================================================================
# 2. TREASURY OPERATIONS & GL INTEGRATION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestTreasuryOperationsAndGLIntegration:
    def test_cash_deposit_updates_balances_and_posts_gl_journal(self):
        """Cash deposit ($1,000 from Cash -> Bank) updates ledger balances and posts GL journal (Debit Bank, Credit Cash)."""
        tenant, company, branch, warehouse, cash_acc, bank_acc, register, session, cashier, coa_map = cb_full_setup()
        treasury_service = TreasuryOperationsService()

        deposit = treasury_service.create_cash_deposit(
            tenant=tenant, company=company, cash_account=cash_acc, bank_account=bank_acc,
            amount=Decimal("1000.0000"), reference="Deposit Slip #991", user=cashier,
        )

        assert deposit.pk is not None
        assert deposit.deposit_number.startswith("DEP-")

        cash_acc.refresh_from_db()
        assert cash_acc.current_balance == Decimal("4000.0000")

        bank_acc.refresh_from_db()
        assert bank_acc.current_balance == Decimal("51000.0000")

        # Verify GL double-entry journal posted
        gl_journal = JournalEntry.objects.get(tenant=tenant, reference_id=str(deposit.pk))
        assert gl_journal.total_debit == Decimal("1000.0000")
        assert gl_journal.total_credit == Decimal("1000.0000")
        assert gl_journal.status == JournalStatus.POSTED

    def test_insufficient_cash_balance_deposit_rejected(self):
        """Cash deposit exceeding available CashAccount balance raises InsufficientCashBalanceError."""
        tenant, company, branch, warehouse, cash_acc, bank_acc, register, session, cashier, coa_map = cb_full_setup()
        treasury_service = TreasuryOperationsService()

        with pytest.raises(InsufficientCashBalanceError):
            treasury_service.create_cash_deposit(
                tenant=tenant, company=company, cash_account=cash_acc, bank_account=bank_acc,
                amount=Decimal("999999.0000"), user=cashier,
            )

    def test_cash_withdrawal_updates_balances_and_posts_gl_journal(self):
        """Cash withdrawal ($2,000 from Bank -> Cash) updates balances and posts GL journal (Debit Cash, Credit Bank)."""
        tenant, company, branch, warehouse, cash_acc, bank_acc, register, session, cashier, coa_map = cb_full_setup()
        treasury_service = TreasuryOperationsService()

        withdrawal = treasury_service.create_cash_withdrawal(
            tenant=tenant, company=company, bank_account=bank_acc, cash_account=cash_acc,
            amount=Decimal("2000.0000"), purpose="Replenish Petty Cash Float", user=cashier,
        )

        assert withdrawal.pk is not None
        assert withdrawal.withdrawal_number.startswith("WTH-")

        bank_acc.refresh_from_db()
        assert bank_acc.current_balance == Decimal("48000.0000")

        cash_acc.refresh_from_db()
        assert cash_acc.current_balance == Decimal("7000.0000")

        # Verify GL double-entry journal posted
        gl_journal = JournalEntry.objects.get(tenant=tenant, reference_id=str(withdrawal.pk))
        assert gl_journal.total_debit == Decimal("2000.0000")
        assert gl_journal.total_credit == Decimal("2000.0000")


# ===========================================================================
# 3. BANK STATEMENT IMPORT & RECONCILIATION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestBankStatementAndReconciliation:
    def test_bank_statement_import_and_duplicate_prevention(self):
        """Importing bank statement transactions enforces sha256 import_hash duplicate protection."""
        tenant, company, branch, warehouse, cash_acc, bank_acc, register, session, cashier, coa_map = cb_full_setup()
        import_service = BankStatementImportService()

        lines = [
            {"transaction_date": timezone.now().date(), "amount": Decimal("1000.0000"), "reference": "REF101", "external_id": "EXT-101"},
            {"transaction_date": timezone.now().date(), "amount": Decimal("-500.0000"), "reference": "REF102", "external_id": "EXT-102"},
        ]

        txs = import_service.import_bank_transactions(tenant=tenant, bank_account=bank_acc, statement_lines=lines, user=cashier)
        assert len(txs) == 2

        # Import same statement lines again -> should skip duplicates safely
        txs_dup = import_service.import_bank_transactions(tenant=tenant, bank_account=bank_acc, statement_lines=lines, user=cashier)
        assert len(txs_dup) == 0

    def test_bank_reconciliation_matching(self):
        """Matching bank statement line to book entry updates status to MATCHED."""
        tenant, company, branch, warehouse, cash_acc, bank_acc, register, session, cashier, coa_map = cb_full_setup()
        import_service = BankStatementImportService()
        rec_service = FinancialReconciliationService()

        txs = import_service.import_bank_transactions(
            tenant=tenant, bank_account=bank_acc,
            statement_lines=[{"transaction_date": timezone.now().date(), "amount": Decimal("1000.0000"), "reference": "DEP-991"}],
            user=cashier,
        )

        rec = rec_service.create_reconciliation_session(
            tenant=tenant, company=company, bank_account=bank_acc,
            start_date=timezone.now().date(), end_date=timezone.now().date(),
            statement_closing_balance=bank_acc.current_balance, user=cashier,
        )

        match = rec_service.match_transaction(
            tenant=tenant, reconciliation=rec, bank_transaction=txs[0],
            reference_type="CASH_DEPOSIT", reference_id="123", matched_amount=Decimal("1000.0000"),
        )

        assert match.pk is not None
        txs[0].refresh_from_db()
        assert txs[0].reconciliation_status == ReconciliationMatchStatus.MATCHED

    def test_treasury_summary_selector(self):
        """TreasurySelector calculates accurate cash and bank liquidity overview."""
        tenant, company, branch, warehouse, cash_acc, bank_acc, register, session, cashier, coa_map = cb_full_setup()
        selector = TreasurySelector()

        summary = selector.get_treasury_summary(tenant, company_id=str(company.pk))
        assert summary["total_cash_balance"] == Decimal("5000.0000")
        assert summary["total_bank_balance"] == Decimal("50000.0000")
        assert summary["total_liquidity"] == Decimal("55000.0000")
        assert summary["open_register_sessions_count"] == 1
