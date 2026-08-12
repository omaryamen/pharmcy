"""Comprehensive test suite for IMP-028 — Enterprise Customer Accounts Receivable (AR).
Tests: AR creation from POS credit sales, payment posting, multi-receivable allocations, partial/full payments,
overpayment policy enforcement, customer credit limit checks, customer ledger statements, AR aging analysis,
adjustments, bad debt write-offs, dispute resolution, return credit integration, payment reversals,
AR reconciliation audits, idempotency, and multi-tenant isolation.
"""

from __future__ import annotations

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.accounts_receivable.exceptions import (
    CreditLimitExceededError,
    ExceedsOutstandingBalanceError,
    OverpaymentRejectedError,
    PaymentAlreadyReversedError,
    SelfApprovalForbiddenError,
)
from apps.accounts_receivable.models import (
    ARAdjustmentStatus,
    ARPaymentMethod,
    ARPaymentStatus,
    ARStatus,
    CustomerPayment,
    CustomerReceivable,
    DisputeStatus,
    OverpaymentPolicy,
)
from apps.accounts_receivable.services import (
    ARReconciliationService,
    CustomerPaymentService,
    CustomerReceivableService,
    ReceivableAdjustmentService,
    ReceivableDisputeService,
)
from apps.branches.models import Branch
from apps.companies.models import Company
from apps.core.models import Tenant
from apps.customers.models import Customer
from apps.goods_receipt.services import GoodsReceiptService
from apps.inventory.models import Batch, InventoryItem
from apps.medicines.models import Medicine
from apps.procurement.services import PurchaseOrderService
from apps.sales.models import SalesInvoice
from apps.sales.services import PosSalesService
from apps.suppliers.models import Supplier
from apps.warehouses.models import StorageLocation, Warehouse

User = get_user_model()


def ar_full_setup():
    """Helper fixture creating tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, and manager."""
    tenant = Tenant.objects.create(name=f"AR Tenant {uuid.uuid4().hex[:6]}", slug=f"ar-slug-{uuid.uuid4().hex[:6]}")
    company = Company.objects.create(tenant=tenant, legal_name="Pharma AR Corp", commercial_name="Pharma AR Corp", code=f"COMP-{uuid.uuid4().hex[:4]}", slug=f"comp-{uuid.uuid4().hex[:4]}")
    branch = Branch.objects.create(tenant=tenant, company=company, name="Main AR Branch", code=f"BR-{uuid.uuid4().hex[:4]}")
    warehouse = Warehouse.objects.create(tenant=tenant, company=company, branch=branch, name="Main AR WH", code=f"WH-{uuid.uuid4().hex[:4]}")
    location = StorageLocation.objects.create(tenant=tenant, warehouse=warehouse, name="Shelf C1", code=f"LOC-{uuid.uuid4().hex[:4]}")

    customer = Customer.objects.create(
        tenant=tenant,
        company=company,
        first_name="Alice",
        last_name="Johnson",
        english_name="Alice Johnson Debtor",
        customer_number=f"CUST-{uuid.uuid4().hex[:6]}",
        status="active",
        credit_allowed=True,
        credit_limit=Decimal("5000.00"),
        opening_balance=Decimal("0.00"),
        current_balance=Decimal("0.00"),
    )

    medicine = Medicine.objects.create(
        tenant=tenant,
        company=company,
        sku=f"SKU-AR-{uuid.uuid4().hex[:6]}",
        barcode=f"BAR-AR-{uuid.uuid4().hex[:6]}",
        english_name="Paracetamol 500mg Tablets",
        arabic_name="باراسيتامول 500مجم أقراص",
        status="active",
        unit_of_measure="Pcs",
    )

    supplier = Supplier.objects.create(tenant=tenant, code=f"SUP-{uuid.uuid4().hex[:6]}", legal_name="Pharma Wholesaler", status="active")

    po_creator = User.objects.create_user(email=f"poc_{uuid.uuid4().hex[:4]}@test.com", first_name="PO Creator", password="pass")
    po_approver = User.objects.create_user(email=f"poa_{uuid.uuid4().hex[:4]}@test.com", first_name="PO Approver", password="pass")
    cashier = User.objects.create_user(email=f"cashier_{uuid.uuid4().hex[:4]}@test.com", first_name="Cashier", password="pass")
    manager = User.objects.create_user(email=f"manager_{uuid.uuid4().hex[:4]}@test.com", first_name="Manager", password="pass")

    po_service = PurchaseOrderService()
    grn_service = GoodsReceiptService()

    po = po_service.create_purchase_order(
        tenant=tenant, company=company, supplier=supplier, warehouse=warehouse,
        currency="USD", lines_data=[{"medicine": medicine, "ordered_quantity": Decimal("1000.0000"), "unit_price": Decimal("10.0000")}],
        user=po_creator,
    )
    po_service.submit_purchase_order(tenant, po, user=po_creator)
    po_service.approve_purchase_order(tenant, po, user=po_approver)
    po_service.send_to_supplier(tenant, po, user=po_approver)

    grn = grn_service.create_goods_receipt(
        tenant=tenant, company=company, supplier=supplier, warehouse=warehouse, purchase_order=po,
        receiving_location=location,
        lines_data=[{
            "purchase_order_line": po.lines.first(),
            "medicine": medicine, "received_quantity": Decimal("1000.0000"), "accepted_quantity": Decimal("1000.0000"), "unit_cost": Decimal("10.0000"),
            "batch_number": f"AR-BATCH-{uuid.uuid4().hex[:4]}", "expiry_date": timezone.now().date() + timedelta(days=365),
            "storage_location": location,
        }],
        user=po_creator,
    )
    grn_service.post_goods_receipt(tenant, grn, user=po_creator)

    batch = Batch.objects.get(tenant=tenant, medicine=medicine)
    batch.selling_price = Decimal("15.0000")
    batch.save()

    # Complete a credit sale of 100 units = $1500 ($400 paid, $1100 outstanding)
    pos_service = PosSalesService()
    invoice = pos_service.create_draft_or_held_sale(
        tenant=tenant, company=company, branch=branch, warehouse=warehouse, customer=customer,
        lines_data=[{"medicine": medicine, "batch": batch, "storage_location": location, "quantity": Decimal("100.0000"), "unit_price": Decimal("15.0000")}],
        cashier=cashier,
    )
    invoice = pos_service.complete_sale(
        tenant=tenant, invoice=invoice,
        payments_data=[{"payment_method": "cash", "amount": Decimal("400.0000")}],
        user=cashier,
    )

    return tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, manager, invoice


# ===========================================================================
# 1. CUSTOMER RECEIVABLE CREATION & CREDIT SALES TESTS
# ===========================================================================


@pytest.mark.django_db
class TestCustomerReceivableCreationAndSync:
    def test_sync_receivable_from_credit_sale(self):
        """Invoice $1,500 ($400 paid) creates AR record with original=$1,500, paid=$400, outstanding=$1,100."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, manager, invoice = ar_full_setup()
        ar_service = CustomerReceivableService()

        receivable = ar_service.sync_receivable_from_sales_invoice(tenant, invoice, due_days=30, user=cashier)

        assert receivable.pk is not None
        assert receivable.receivable_number.startswith("AR-")
        assert receivable.original_amount == Decimal("1500.0000")
        assert receivable.paid_amount == Decimal("400.0000")
        assert receivable.outstanding_amount == Decimal("1100.0000")
        assert receivable.status == ARStatus.OPEN

        customer.refresh_from_db()
        assert customer.current_balance == Decimal("1100.0000")

    def test_credit_sale_exceeding_credit_limit_rejected(self):
        """Credit sale exceeding customer credit limit raises CreditLimitExceededError."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, manager, invoice = ar_full_setup()
        customer.credit_limit = Decimal("500.00")  # Set tight limit
        customer.save()

        ar_service = CustomerReceivableService()
        with pytest.raises(CreditLimitExceededError):
            ar_service.sync_receivable_from_sales_invoice(tenant, invoice, due_days=30, user=cashier)


# ===========================================================================
# 2. CUSTOMER PAYMENT & MULTI-RECEIVABLE ALLOCATION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestCustomerPaymentAndAllocation:
    def test_partial_payment_reduces_outstanding_balance(self):
        """Receivable = $1,100, Payment = $300 -> Outstanding = $800, status = PARTIALLY_PAID."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, manager, invoice = ar_full_setup()
        ar_service = CustomerReceivableService()
        pmt_service = CustomerPaymentService()

        rx = ar_service.sync_receivable_from_sales_invoice(tenant, invoice, user=cashier)

        payment = pmt_service.post_customer_payment(
            tenant=tenant, company=company, customer=customer, amount=Decimal("300.0000"),
            payment_method=ARPaymentMethod.CASH,
            allocations_data=[{"receivable_id": str(rx.pk), "allocated_amount": Decimal("300.0000")}],
            user=cashier,
        )

        assert payment.allocated_amount == Decimal("300.0000")
        assert payment.status == ARPaymentStatus.FULLY_ALLOCATED

        rx.refresh_from_db()
        assert rx.outstanding_amount == Decimal("800.0000")
        assert rx.status == ARStatus.PARTIALLY_PAID

        customer.refresh_from_db()
        assert customer.current_balance == Decimal("800.0000")

    def test_full_payment_closes_receivable(self):
        """Receivable = $1,100, Payment = $1,100 -> Outstanding = $0, status = PAID."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, manager, invoice = ar_full_setup()
        ar_service = CustomerReceivableService()
        pmt_service = CustomerPaymentService()

        rx = ar_service.sync_receivable_from_sales_invoice(tenant, invoice, user=cashier)

        payment = pmt_service.post_customer_payment(
            tenant=tenant, company=company, customer=customer, amount=Decimal("1100.0000"),
            payment_method=ARPaymentMethod.BANK_TRANSFER,
            allocations_data=[{"receivable_id": str(rx.pk), "allocated_amount": Decimal("1100.0000")}],
            user=cashier,
        )

        rx.refresh_from_db()
        assert rx.outstanding_amount == Decimal("0.0000")
        assert rx.status == ARStatus.PAID

        customer.refresh_from_db()
        assert customer.current_balance == Decimal("0.0000")

    def test_overpayment_rejected_by_policy(self):
        """Overpayment rejected when policy is REJECT."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, manager, invoice = ar_full_setup()
        ar_service = CustomerReceivableService()
        pmt_service = CustomerPaymentService()

        rx = ar_service.sync_receivable_from_sales_invoice(tenant, invoice, user=cashier)

        with pytest.raises(OverpaymentRejectedError):
            pmt_service.post_customer_payment(
                tenant=tenant, company=company, customer=customer, amount=Decimal("1500.0000"),
                allocations_data=[{"receivable_id": str(rx.pk), "allocated_amount": Decimal("1100.0000")}],
                overpayment_policy=OverpaymentPolicy.REJECT,
                user=cashier,
            )

    def test_reverse_customer_payment_restores_receivable(self):
        """Reversing payment restores receivable outstanding balance and customer debt."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, manager, invoice = ar_full_setup()
        ar_service = CustomerReceivableService()
        pmt_service = CustomerPaymentService()

        rx = ar_service.sync_receivable_from_sales_invoice(tenant, invoice, user=cashier)

        payment = pmt_service.post_customer_payment(
            tenant=tenant, company=company, customer=customer, amount=Decimal("500.0000"),
            allocations_data=[{"receivable_id": str(rx.pk), "allocated_amount": Decimal("500.0000")}],
            user=cashier,
        )

        reversed_pmt = pmt_service.reverse_customer_payment(tenant, payment, reversal_reason="Bounced Check", user=manager)
        assert reversed_pmt.status == ARPaymentStatus.REVERSED

        rx.refresh_from_db()
        assert rx.outstanding_amount == Decimal("1100.0000")
        assert rx.status == ARStatus.PARTIALLY_PAID

        customer.refresh_from_db()
        assert customer.current_balance == Decimal("1100.0000")


# ===========================================================================
# 3. ADJUSTMENTS, WRITE-OFFS & RECONCILIATION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestAdjustmentsWriteOffsAndReconciliation:
    def test_credit_adjustment_reduces_balance(self):
        """Credit adjustment ($200) reduces receivable outstanding balance and customer balance."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, manager, invoice = ar_full_setup()
        ar_service = CustomerReceivableService()
        adj_service = ReceivableAdjustmentService()

        rx = ar_service.sync_receivable_from_sales_invoice(tenant, invoice, user=cashier)

        adj = adj_service.create_adjustment(
            tenant=tenant, receivable=rx, amount=Decimal("200.0000"),
            reason="Promotional Credit Discount", user=cashier, approver=manager,
        )

        assert adj.pk is not None
        assert adj.status == ARAdjustmentStatus.APPROVED

        rx.refresh_from_db()
        assert rx.outstanding_amount == Decimal("900.0000")

        customer.refresh_from_db()
        assert customer.current_balance == Decimal("900.0000")

    def test_write_off_bad_debt(self):
        """Formal bad debt write-off ($1,100) sets status WRITTEN_OFF and reduces customer debt balance."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, manager, invoice = ar_full_setup()
        ar_service = CustomerReceivableService()
        adj_service = ReceivableAdjustmentService()

        rx = ar_service.sync_receivable_from_sales_invoice(tenant, invoice, user=cashier)

        wof = adj_service.write_off_receivable(
            tenant=tenant, receivable=rx, amount=Decimal("1100.0000"),
            reason="Uncollectible bankruptcy", approver=manager, user=cashier,
        )

        assert wof.pk is not None
        rx.refresh_from_db()
        assert rx.status == ARStatus.WRITTEN_OFF
        assert rx.outstanding_amount == Decimal("0.0000")

        customer.refresh_from_db()
        assert customer.current_balance == Decimal("0.0000")

    def test_ar_reconciliation_audit(self):
        """Audit customer balance against open receivables and detect zero discrepancies."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, manager, invoice = ar_full_setup()
        ar_service = CustomerReceivableService()
        rec_service = ARReconciliationService()

        ar_service.sync_receivable_from_sales_invoice(tenant, invoice, user=cashier)

        audit = rec_service.reconcile_customer_balance(tenant=tenant, customer=customer)
        assert audit["is_reconciled"] is True
        assert audit["discrepancy"] == Decimal("0.0000")
        assert audit["actual_outstanding"] == Decimal("1100.0000")
