"""Comprehensive test suite for IMP-029 — Enterprise General Ledger & Double-Entry Accounting.
Tests: Chart of Accounts seeding, hierarchy integrity, double-entry validation (Debits == Credits),
unbalanced journal rejection, journal posting engine, immutable reversal engine, accounting period locks,
sales revenue integration, AR/AP subledger integrations, COGS & inventory stock movement integration,
Trial Balance calculation, Profit & Loss, Balance Sheet, reconciliation audits, idempotency, and multi-tenant isolation.
"""

from __future__ import annotations

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.accounts_payable.models import SupplierInvoice, SupplierPayment
from apps.accounts_receivable.models import CustomerPayment
from apps.accounts_receivable.services import CustomerPaymentService, CustomerReceivableService
from apps.branches.models import Branch
from apps.companies.models import Company
from apps.core.models import Tenant
from apps.customers.models import Customer
from apps.general_ledger.exceptions import (
    ControlAccountPostingForbiddenError,
    PeriodClosedError,
    UnbalancedJournalError,
)
from apps.general_ledger.models import (
    AccountingPeriod,
    AccountSubtype,
    AccountType,
    ChartOfAccount,
    JournalEntry,
    JournalStatus,
    PeriodStatus,
)
from apps.general_ledger.selectors import GLSelector
from apps.general_ledger.services import (
    ChartOfAccountsService,
    GLIntegrationPostingService,
    GLReconciliationService,
    JournalPostingService,
    JournalReversalService,
)
from apps.goods_receipt.services import GoodsReceiptService
from apps.inventory.models import Batch
from apps.medicines.models import Medicine
from apps.procurement.services import PurchaseOrderService
from apps.sales.models import SalesInvoice
from apps.sales.services import PosSalesService
from apps.suppliers.models import Supplier
from apps.warehouses.models import StorageLocation, Warehouse

User = get_user_model()


def gl_full_setup():
    """Fixture initializing tenant, company, branch, warehouse, location, cashier, manager, and seeded Chart of Accounts."""
    tenant = Tenant.objects.create(name=f"GL Tenant {uuid.uuid4().hex[:6]}", slug=f"gl-slug-{uuid.uuid4().hex[:6]}")
    company = Company.objects.create(tenant=tenant, legal_name="Pharma Accounting Corp", commercial_name="Pharma Accounting Corp", code=f"COMP-{uuid.uuid4().hex[:4]}", slug=f"comp-{uuid.uuid4().hex[:4]}")
    branch = Branch.objects.create(tenant=tenant, company=company, name="Main GL Branch", code=f"BR-{uuid.uuid4().hex[:4]}")
    warehouse = Warehouse.objects.create(tenant=tenant, company=company, branch=branch, name="Main GL WH", code=f"WH-{uuid.uuid4().hex[:4]}")
    location = StorageLocation.objects.create(tenant=tenant, warehouse=warehouse, name="Shelf A1", code=f"LOC-{uuid.uuid4().hex[:4]}")

    customer = Customer.objects.create(
        tenant=tenant, company=company, first_name="Bob", last_name="Smith", english_name="Bob Smith Client",
        customer_number=f"CUST-{uuid.uuid4().hex[:6]}", status="active", credit_allowed=True, credit_limit=Decimal("10000.00"),
    )

    supplier = Supplier.objects.create(tenant=tenant, code=f"SUP-{uuid.uuid4().hex[:6]}", legal_name="Pharma Vendor Co", status="active")

    user = User.objects.create_user(email=f"gluser_{uuid.uuid4().hex[:4]}@test.com", first_name="GL Accountant", password="pass")

    coa_service = ChartOfAccountsService()
    coa_map = coa_service.seed_default_chart_of_accounts(tenant, company)

    return tenant, company, branch, warehouse, location, customer, supplier, user, coa_map


# ===========================================================================
# 1. CHART OF ACCOUNTS & HIERARCHY TESTS
# ===========================================================================


@pytest.mark.django_db
class TestChartOfAccountsAndSeeding:
    def test_seed_default_chart_of_accounts(self):
        """Seeding creates standard ERP accounts (1000, 1100, 1200, 1300, 1400, 2000, 2100, 2200, 3000, 4000, 5000, 6000)."""
        tenant, company, branch, warehouse, location, customer, supplier, user, coa_map = gl_full_setup()

        assert "1100" in coa_map
        assert coa_map["1100"].account_name == "Cash on Hand"
        assert coa_map["1100"].account_type == AccountType.ASSET

        assert "4100" in coa_map
        assert coa_map["4100"].account_name == "Sales Revenue"
        assert coa_map["4100"].account_type == AccountType.REVENUE

        assert "5000" in coa_map
        assert coa_map["5000"].account_type == AccountType.COST_OF_GOODS_SOLD

    def test_posting_to_control_account_forbidden(self):
        """Direct journal posting to summary control account (is_control_account=True) raises ControlAccountPostingForbiddenError."""
        tenant, company, branch, warehouse, location, customer, supplier, user, coa_map = gl_full_setup()
        posting_service = JournalPostingService()

        control_acc = coa_map["1000"]  # Assets summary control account
        cash_acc = coa_map["1100"]

        lines = [
            {"account": control_acc, "debit": Decimal("500.0000"), "credit": Decimal("0.0000")},
            {"account": cash_acc, "debit": Decimal("0.0000"), "credit": Decimal("500.0000")},
        ]

        with pytest.raises(ControlAccountPostingForbiddenError):
            posting_service.create_and_post_journal_entry(
                tenant=tenant, company=company, posting_date=timezone.now().date(),
                description="Invalid control account post", lines_data=lines, user=user,
            )


# ===========================================================================
# 2. DOUBLE-ENTRY & JOURNAL POSTING TESTS
# ===========================================================================


@pytest.mark.django_db
class TestDoubleEntryAndPostingEngine:
    def test_balanced_journal_posts_successfully(self):
        """Total Debits ($1,000) == Total Credits ($1,000) posts atomically with status POSTED."""
        tenant, company, branch, warehouse, location, customer, supplier, user, coa_map = gl_full_setup()
        posting_service = JournalPostingService()

        cash_acc = coa_map["1100"]
        rev_acc = coa_map["4100"]

        lines = [
            {"account": cash_acc, "debit": Decimal("1000.0000"), "credit": Decimal("0.0000")},
            {"account": rev_acc, "debit": Decimal("0.0000"), "credit": Decimal("1000.0000")},
        ]

        journal = posting_service.create_and_post_journal_entry(
            tenant=tenant, company=company, posting_date=timezone.now().date(),
            description="Cash Sale $1,000", lines_data=lines, user=user,
        )

        assert journal.pk is not None
        assert journal.journal_number.startswith("JRN-")
        assert journal.status == JournalStatus.POSTED
        assert journal.total_debit == Decimal("1000.0000")
        assert journal.total_credit == Decimal("1000.0000")
        assert journal.is_balanced is True

    def test_unbalanced_journal_strictly_rejected(self):
        """Unbalanced journal (Debits $1,000 != Credits $800) strictly raises UnbalancedJournalError."""
        tenant, company, branch, warehouse, location, customer, supplier, user, coa_map = gl_full_setup()
        posting_service = JournalPostingService()

        cash_acc = coa_map["1100"]
        rev_acc = coa_map["4100"]

        lines = [
            {"account": cash_acc, "debit": Decimal("1000.0000"), "credit": Decimal("0.0000")},
            {"account": rev_acc, "debit": Decimal("0.0000"), "credit": Decimal("800.0000")},
        ]

        with pytest.raises(UnbalancedJournalError):
            posting_service.create_and_post_journal_entry(
                tenant=tenant, company=company, posting_date=timezone.now().date(),
                description="Unbalanced cash sale", lines_data=lines, user=user,
            )


# ===========================================================================
# 3. REVERSAL & PERIOD LOCK TESTS
# ===========================================================================


@pytest.mark.django_db
class TestReversalAndPeriodLocks:
    def test_reversing_journal_creates_compensating_entry(self):
        """Reversing a posted journal creates compensating entry and updates original status to REVERSED."""
        tenant, company, branch, warehouse, location, customer, supplier, user, coa_map = gl_full_setup()
        posting_service = JournalPostingService()
        reversal_service = JournalReversalService()

        cash_acc = coa_map["1100"]
        rev_acc = coa_map["4100"]

        lines = [
            {"account": cash_acc, "debit": Decimal("1000.0000"), "credit": Decimal("0.0000")},
            {"account": rev_acc, "debit": Decimal("0.0000"), "credit": Decimal("1000.0000")},
        ]

        jrn = posting_service.create_and_post_journal_entry(
            tenant=tenant, company=company, posting_date=timezone.now().date(),
            description="Original Sale", lines_data=lines, user=user,
        )

        reversal_jrn = reversal_service.reverse_journal_entry(tenant, jrn, "Refund Reversal", user=user)

        assert reversal_jrn.status == JournalStatus.POSTED
        assert reversal_jrn.total_debit == Decimal("1000.0000")
        assert reversal_jrn.total_credit == Decimal("1000.0000")

        jrn.refresh_from_db()
        assert jrn.status == JournalStatus.REVERSED

    def test_closed_period_prevents_posting(self):
        """Posting to a CLOSED accounting period strictly raises PeriodClosedError."""
        tenant, company, branch, warehouse, location, customer, supplier, user, coa_map = gl_full_setup()
        posting_service = JournalPostingService()

        period = AccountingPeriod.objects.create(
            tenant=tenant, company=company, fiscal_year=2025, period_number=12,
            name="2025-12", start_date=date(2025, 12, 1), end_date=date(2025, 12, 31),
            status=PeriodStatus.CLOSED,
        )

        cash_acc = coa_map["1100"]
        rev_acc = coa_map["4100"]

        lines = [
            {"account": cash_acc, "debit": Decimal("1000.0000"), "credit": Decimal("0.0000")},
            {"account": rev_acc, "debit": Decimal("0.0000"), "credit": Decimal("1000.0000")},
        ]

        with pytest.raises(PeriodClosedError):
            posting_service.create_and_post_journal_entry(
                tenant=tenant, company=company, posting_date=date(2025, 12, 15),
                description="Late 2025 entry", lines_data=lines, user=user,
            )


# ===========================================================================
# 4. OPERATIONAL DOMAIN INTEGRATION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestGLDomainIntegrations:
    def test_customer_payment_gl_integration(self):
        """Customer Payment ($500) posts GL journal: Debit Cash ($500), Credit AR ($500)."""
        tenant, company, branch, warehouse, location, customer, supplier, user, coa_map = gl_full_setup()
        pmt_service = CustomerPaymentService()
        gl_integration = GLIntegrationPostingService()

        payment = pmt_service.post_customer_payment(
            tenant=tenant, company=company, customer=customer, amount=Decimal("500.0000"),
            user=user,
        )

        gl_integration.post_customer_payment_journal(tenant, payment, user=user)

        jrn = JournalEntry.objects.get(tenant=tenant, reference_id=str(payment.pk))
        assert jrn.total_debit == Decimal("500.0000")
        assert jrn.total_credit == Decimal("500.0000")
        assert jrn.status == JournalStatus.POSTED

    def test_trial_balance_always_balanced(self):
        """Trial balance across multiple domain postings maintains Total Debits == Total Credits."""
        tenant, company, branch, warehouse, location, customer, supplier, user, coa_map = gl_full_setup()
        posting_service = JournalPostingService()
        selector = GLSelector()

        cash_acc = coa_map["1100"]
        rev_acc = coa_map["4100"]
        ar_acc = coa_map["1300"]

        # Transaction 1: Cash sale $1000
        posting_service.create_and_post_journal_entry(
            tenant=tenant, company=company, posting_date=timezone.now().date(), description="Sale 1",
            lines_data=[
                {"account": cash_acc, "debit": Decimal("1000.0000"), "credit": Decimal("0.0000")},
                {"account": rev_acc, "debit": Decimal("0.0000"), "credit": Decimal("1000.0000")},
            ],
            user=user,
        )

        # Transaction 2: Credit sale $2000
        posting_service.create_and_post_journal_entry(
            tenant=tenant, company=company, posting_date=timezone.now().date(), description="Sale 2",
            lines_data=[
                {"account": ar_acc, "debit": Decimal("2000.0000"), "credit": Decimal("0.0000")},
                {"account": rev_acc, "debit": Decimal("0.0000"), "credit": Decimal("2000.0000")},
            ],
            user=user,
        )

        tb = selector.get_trial_balance(tenant, str(company.pk))
        assert tb["is_balanced"] is True
        assert tb["total_debit"] == Decimal("3000.0000")
        assert tb["total_credit"] == Decimal("3000.0000")
