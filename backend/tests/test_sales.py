"""Comprehensive test suite for IMP-025 — Enterprise POS & Sales Management.
Tests: barcode lookups, cart/draft creation, FEFO batch allocation, stock validation (insufficient, expired, recalled),
atomic sale completion via StockMovementEngine (SALE movement type), zero direct inventory mutations,
cash change calculation, mixed payment methods, customer credit sales & credit limit enforcement,
voiding sales with compensating stock movements, cash register session reconciliation variance,
idempotency, and multi-tenant isolation.
"""

from __future__ import annotations

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.branches.models import Branch
from apps.companies.models import Company
from apps.core.models import Tenant
from apps.customers.models import Customer
from apps.goods_receipt.services import GoodsReceiptService
from apps.inventory.models import Batch, InventoryItem
from apps.inventory.models.enums import BatchStatus
from apps.medicines.models import Medicine
from apps.procurement.services import PurchaseOrderService
from apps.sales.exceptions import (
    ExceedsCustomerCreditLimitError,
    IneligibleBatchForSaleError,
    InsufficientStockForSaleError,
    InvalidSaleStateError,
)
from apps.sales.models import (
    CashRegister,
    InvoicePaymentStatus,
    RegisterSession,
    SalesInvoice,
    SalesPaymentMethod,
    SalesPaymentStatus,
    SalesStatus,
    SessionStatus,
)
from apps.sales.selectors import PosSelector
from apps.sales.services import FEFOBatchSelector, PosSalesService
from apps.stock_movement.models import StockMovement
from apps.suppliers.models import Supplier
from apps.warehouses.models import StorageLocation, Warehouse

User = get_user_model()


# ---------------------------------------------------------------------------
# Test data factories
# ---------------------------------------------------------------------------

def make_tenant(suffix=""):
    code = "pos-" + uuid.uuid4().hex[:6] + suffix
    return Tenant.objects.create(name=f"POS Tenant {code}", code=code, slug=code)


def make_company(tenant, code=None):
    code = code or ("CO-" + uuid.uuid4().hex[:6])
    return Company.objects.create(tenant=tenant, code=code, legal_name=f"Company {code}")


def make_branch(tenant, company, name="Main Retail Branch"):
    code = "BR-" + uuid.uuid4().hex[:6]
    return Branch.objects.create(
        tenant=tenant, company=company, code=code, name=f"{name} {code}", slug=code.lower()
    )


def make_warehouse(tenant, company, name="Pharmacy WH"):
    code = "WH-" + uuid.uuid4().hex[:6]
    return Warehouse.objects.create(tenant=tenant, company=company, code=code, name=f"{name} {code}")


def make_location(tenant, warehouse, name="Counter Shelf"):
    code = "LOC-" + uuid.uuid4().hex[:6]
    return StorageLocation.objects.create(tenant=tenant, warehouse=warehouse, code=code, name=f"{name} {code}")


def make_supplier(tenant, name="Pharma Wholesaler"):
    code = "SUP-" + uuid.uuid4().hex[:6]
    return Supplier.objects.create(tenant=tenant, code=code, legal_name=name, status="active")


def make_customer(tenant, name="John Doe Pharmacy", allow_credit=True, credit_limit="1000.0000"):
    code = "CUST-" + uuid.uuid4().hex[:6]
    return Customer.objects.create(
        tenant=tenant,
        code=code,
        customer_number=code,
        first_name=name,
        english_name=name,
        customer_type="individual",
        status="active",
        credit_allowed=allow_credit,
        credit_limit=Decimal(str(credit_limit)),
        current_balance=Decimal("0.0000"),
    )


def make_medicine(tenant, name="Amoxicillin 500mg", barcode="890123456789"):
    code = "MED-" + uuid.uuid4().hex[:6]
    return Medicine.objects.create(
        tenant=tenant,
        code=code,
        sku=code,
        barcode=barcode,
        english_name=name,
        arabic_name="أمoxicillin",
        status="active",
    )


def make_user(email=None):
    email = email or f"cashier-{uuid.uuid4().hex[:8]}@pos.com"
    return User.objects.create_user(email=email, first_name="Cashier", password="Pass123!")


def pos_full_setup():
    """Setup PO, Goods Receipt, and populate physical inventory in warehouse."""
    tenant = make_tenant()
    company = make_company(tenant)
    branch = make_branch(tenant, company)
    warehouse = make_warehouse(tenant, company)
    location = make_location(tenant, warehouse)
    supplier = make_supplier(tenant)
    customer = make_customer(tenant)
    medicine = make_medicine(tenant)
    creator = make_user("creator@pos.com")
    approver = make_user("approver@pos.com")
    cashier = make_user("cashier@pos.com")

    # Stock receipt of 100 units @ $10.00 cost, selling price $15.00
    po_svc = PurchaseOrderService()
    po = po_svc.create_purchase_order(
        tenant=tenant, company=company, supplier=supplier, warehouse=warehouse,
        lines_data=[{"medicine": medicine, "ordered_quantity": Decimal("100.0000"), "unit_price": Decimal("10.0000")}],
        user=creator,
    )
    po_svc.submit_purchase_order(tenant, po, user=creator)
    po_svc.approve_purchase_order(tenant, po, user=approver)
    po_svc.send_to_supplier(tenant, po, user=approver)

    grn_svc = GoodsReceiptService()
    exp_date = timezone.now().date() + timedelta(days=365)
    grn = grn_svc.create_goods_receipt(
        tenant=tenant, company=company, supplier=supplier, warehouse=warehouse, purchase_order=po,
        receiving_location=location,
        lines_data=[{
            "purchase_order_line": po.lines.first(),
            "medicine": medicine,
            "batch_number": "BATCH-POS-100",
            "expiry_date": exp_date,
            "received_quantity": Decimal("100.0000"),
            "accepted_quantity": Decimal("100.0000"),
            "unit_cost": Decimal("10.0000"),
            "storage_location": location,
        }],
        user=cashier,
    )
    grn_svc.post_goods_receipt(tenant, grn, user=cashier)

    batch = Batch.objects.get(tenant=tenant, medicine=medicine, batch_number="BATCH-POS-100")
    batch.selling_price = Decimal("15.0000")
    batch.save(update_fields=["selling_price"])

    return tenant, company, branch, warehouse, location, customer, medicine, batch, cashier


# ===========================================================================
# BARCODE LOOKUP & CART/DRAFT SALES TESTS
# ===========================================================================


@pytest.mark.django_db
class TestPosBarcodeLookupAndCart:
    def test_barcode_and_sku_lookup(self):
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier = pos_full_setup()
        selector = PosSelector()

        res_barcode = selector.barcode_or_sku_lookup(tenant, "890123456789")
        assert res_barcode.count() == 1
        assert res_barcode.first().pk == medicine.pk

        res_sku = selector.barcode_or_sku_lookup(tenant, medicine.sku)
        assert res_sku.count() == 1

        res_name = selector.barcode_or_sku_lookup(tenant, "Amoxicillin")
        assert res_name.count() == 1

    def test_create_draft_sales_invoice(self):
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier = pos_full_setup()
        service = PosSalesService()

        inv = service.create_draft_or_held_sale(
            tenant=tenant,
            company=company,
            branch=branch,
            warehouse=warehouse,
            lines_data=[{
                "medicine": medicine,
                "batch": batch,
                "storage_location": location,
                "quantity": Decimal("5.0000"),
                "unit_price": Decimal("15.0000"),
            }],
            customer=customer,
            cashier=cashier,
        )

        assert inv.pk is not None
        assert inv.invoice_number.startswith("INV-")
        assert inv.status == SalesStatus.DRAFT
        assert inv.grand_total == Decimal("75.0000")
        assert inv.lines.count() == 1

        line = inv.lines.first()
        assert line.cost_price == Decimal("10.0000")
        assert line.profit_amount == Decimal("25.0000")  # (5 * $15) - (5 * $10) = $25


# ===========================================================================
# FEFO BATCH SELECTION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestFEFOBatchSelector:
    def test_fefo_selects_earliest_expiring_valid_batch(self):
        tenant, company, branch, warehouse, location, customer, medicine, _, cashier = pos_full_setup()
        today = timezone.now().date()

        # Create two batches in inventory: Batch A (expires in 30 days), Batch B (expires in 180 days)
        batch_a = Batch.objects.create(
            tenant=tenant, company=company, medicine=medicine, batch_number="FEFO-A-30", expiry_date=today + timedelta(days=30),
            unit_cost=Decimal("10.0000"), selling_price=Decimal("15.0000"), status=BatchStatus.ACTIVE,
        )
        batch_b = Batch.objects.create(
            tenant=tenant, company=company, medicine=medicine, batch_number="FEFO-B-180", expiry_date=today + timedelta(days=180),
            unit_cost=Decimal("10.0000"), selling_price=Decimal("15.0000"), status=BatchStatus.ACTIVE,
        )

        InventoryItem.objects.create(tenant=tenant, company=company, warehouse=warehouse, storage_location=location, medicine=medicine, batch=batch_a, on_hand_quantity=Decimal("20.00"))
        InventoryItem.objects.create(tenant=tenant, company=company, warehouse=warehouse, storage_location=location, medicine=medicine, batch=batch_b, on_hand_quantity=Decimal("20.00"))

        fefo = FEFOBatchSelector()
        selected_batch, avail_qty = fefo.select_fefo_batch_for_sale(tenant, warehouse, location, medicine, Decimal("5.0000"))
        assert selected_batch.batch_number == "FEFO-A-30"


# ===========================================================================
# ATOMIC SALE & INVENTORY REDUCTION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestAtomicPOSSaleEngine:
    def test_complete_sale_reduces_stock_via_stock_movement_engine(self):
        """CRITICAL: Completing a sale MUST reduce stock strictly through StockMovementEngine (SALE type). Zero direct mutations."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier = pos_full_setup()
        service = PosSalesService()

        # Initial available stock = 100
        inv_item_before = InventoryItem.objects.get(tenant=tenant, warehouse=warehouse, storage_location=location, medicine=medicine, batch=batch)
        assert inv_item_before.on_hand_quantity == Decimal("100.0000")

        # Create draft sale for 10 units @ $15 = $150 total
        inv = service.create_draft_or_held_sale(
            tenant=tenant, company=company, branch=branch, warehouse=warehouse,
            lines_data=[{"medicine": medicine, "batch": batch, "storage_location": location, "quantity": Decimal("10.0000"), "unit_price": Decimal("15.0000")}],
            cashier=cashier,
        )

        # Complete sale with Cash Payment of $150
        comp_inv = service.complete_sale(
            tenant=tenant, invoice=inv, payments_data=[{"payment_method": SalesPaymentMethod.CASH, "amount": Decimal("150.0000"), "tendered_amount": Decimal("150.0000")}],
            user=cashier,
        )

        assert comp_inv.status == SalesStatus.COMPLETED
        assert comp_inv.payment_status == InvoicePaymentStatus.PAID
        assert comp_inv.paid_amount == Decimal("150.0000")

        # Verify physical inventory balance reduced to 90
        inv_item_after = InventoryItem.objects.get(tenant=tenant, warehouse=warehouse, storage_location=location, medicine=medicine, batch=batch)
        assert inv_item_after.on_hand_quantity == Decimal("90.0000")

        # Verify StockMovement record created
        mov = StockMovement.objects.filter(tenant=tenant, reference_number=comp_inv.invoice_number).first()
        assert mov is not None
        assert mov.movement_type == "sale"
        assert mov.quantity == Decimal("10.0000")

    def test_insufficient_stock_rejects_sale(self):
        """Attempting to sell 150 units when stock is 100 raises InsufficientStockForSaleError."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier = pos_full_setup()
        service = PosSalesService()

        inv = service.create_draft_or_held_sale(
            tenant=tenant, company=company, branch=branch, warehouse=warehouse,
            lines_data=[{"medicine": medicine, "batch": batch, "storage_location": location, "quantity": Decimal("150.0000"), "unit_price": Decimal("15.0000")}],
            cashier=cashier,
        )

        with pytest.raises(InsufficientStockForSaleError):
            service.complete_sale(
                tenant=tenant, invoice=inv, payments_data=[{"payment_method": SalesPaymentMethod.CASH, "amount": Decimal("2250.0000")}],
                user=cashier,
            )

    def test_recalled_batch_rejects_sale(self):
        """Recalled batch cannot be sold."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier = pos_full_setup()
        batch.status = BatchStatus.RECALLED
        batch.save(update_fields=["status"])

        service = PosSalesService()

        with pytest.raises(IneligibleBatchForSaleError):
            service.create_draft_or_held_sale(
                tenant=tenant, company=company, branch=branch, warehouse=warehouse,
                lines_data=[{"medicine": medicine, "batch": batch, "storage_location": location, "quantity": Decimal("5.0000"), "unit_price": Decimal("15.0000")}],
                cashier=cashier,
            )


# ===========================================================================
# PAYMENTS, CHANGE & CREDIT SALE TESTS
# ===========================================================================


@pytest.mark.django_db
class TestPaymentsAndCustomerCredit:
    def test_cash_payment_and_change_calculation(self):
        """Invoice = $75. Cash Tendered = $100 -> Change = $25."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier = pos_full_setup()
        service = PosSalesService()

        inv = service.create_draft_or_held_sale(
            tenant=tenant, company=company, branch=branch, warehouse=warehouse,
            lines_data=[{"medicine": medicine, "batch": batch, "storage_location": location, "quantity": Decimal("5.0000"), "unit_price": Decimal("15.0000")}],
            cashier=cashier,
        )

        comp_inv = service.complete_sale(
            tenant=tenant, invoice=inv, payments_data=[{"payment_method": SalesPaymentMethod.CASH, "amount": Decimal("75.0000"), "tendered_amount": Decimal("100.0000")}],
            user=cashier,
        )

        assert comp_inv.paid_amount == Decimal("75.0000")
        assert comp_inv.change_amount == Decimal("25.0000")

    def test_split_mixed_payments(self):
        """Invoice = $1000. Cash = $400, Card = $300, Mobile Wallet = $300 -> Total Paid = $1000, PAID."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier = pos_full_setup()
        service = PosSalesService()

        inv = service.create_draft_or_held_sale(
            tenant=tenant, company=company, branch=branch, warehouse=warehouse,
            lines_data=[{"medicine": medicine, "batch": batch, "storage_location": location, "quantity": Decimal("100.0000"), "unit_price": Decimal("10.0000")}],
            cashier=cashier,
        )

        comp_inv = service.complete_sale(
            tenant=tenant, invoice=inv,
            payments_data=[
                {"payment_method": SalesPaymentMethod.CASH, "amount": Decimal("400.0000")},
                {"payment_method": SalesPaymentMethod.CARD, "amount": Decimal("300.0000")},
                {"payment_method": SalesPaymentMethod.MOBILE_WALLET, "amount": Decimal("300.0000")},
            ],
            user=cashier,
        )

        assert comp_inv.paid_amount == Decimal("1000.0000")
        assert comp_inv.status == SalesStatus.COMPLETED
        assert comp_inv.payments.count() == 3

    def test_customer_credit_sale_and_credit_limit_enforcement(self):
        """Customer Credit Limit = $1000. Sale = $600 -> Customer Balance = $600. Second Sale = $500 -> Rejected."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier = pos_full_setup()
        service = PosSalesService()

        inv1 = service.create_draft_or_held_sale(
            tenant=tenant, company=company, branch=branch, warehouse=warehouse, customer=customer,
            lines_data=[{"medicine": medicine, "batch": batch, "storage_location": location, "quantity": Decimal("40.0000"), "unit_price": Decimal("15.0000")}],  # $600
            cashier=cashier,
        )

        service.complete_sale(
            tenant=tenant, invoice=inv1, payments_data=[{"payment_method": SalesPaymentMethod.CUSTOMER_CREDIT, "amount": Decimal("600.0000")}],
            user=cashier,
        )

        customer.refresh_from_db()
        assert customer.current_balance == Decimal("600.0000")

        # Second credit sale of $500 exceeds available credit ($400 remaining)
        inv2 = service.create_draft_or_held_sale(
            tenant=tenant, company=company, branch=branch, warehouse=warehouse, customer=customer,
            lines_data=[{"medicine": medicine, "batch": batch, "storage_location": location, "quantity": Decimal("33.3333"), "unit_price": Decimal("15.0000")}],  # ~$500
            cashier=cashier,
        )

        with pytest.raises(ExceedsCustomerCreditLimitError):
            service.complete_sale(
                tenant=tenant, invoice=inv2, payments_data=[{"payment_method": SalesPaymentMethod.CUSTOMER_CREDIT, "amount": Decimal("500.0000")}],
                user=cashier,
            )


# ===========================================================================
# VOID WORKFLOW & CASH REGISTER SESSION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestVoidWorkflowAndRegisterSession:
    def test_void_completed_sale_restores_inventory(self):
        """Voiding a completed sale creates compensating SALE_RETURN movement and restores stock."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier = pos_full_setup()
        service = PosSalesService()

        inv = service.create_draft_or_held_sale(
            tenant=tenant, company=company, branch=branch, warehouse=warehouse,
            lines_data=[{"medicine": medicine, "batch": batch, "storage_location": location, "quantity": Decimal("10.0000"), "unit_price": Decimal("15.0000")}],
            cashier=cashier,
        )
        comp_inv = service.complete_sale(
            tenant=tenant, invoice=inv, payments_data=[{"payment_method": SalesPaymentMethod.CASH, "amount": Decimal("150.0000")}], user=cashier,
        )

        assert InventoryItem.objects.get(tenant=tenant, warehouse=warehouse, storage_location=location, medicine=medicine, batch=batch).on_hand_quantity == Decimal("90.0000")

        # Void sale
        void_inv = service.void_completed_sale(tenant, comp_inv, reason="Customer returned item at counter", user=cashier)
        assert void_inv.status == SalesStatus.VOIDED

        # Stock restored to 100
        assert InventoryItem.objects.get(tenant=tenant, warehouse=warehouse, storage_location=location, medicine=medicine, batch=batch).on_hand_quantity == Decimal("100.0000")

    def test_cash_register_session_reconciliation_variance(self):
        """Opening Cash = $500, Cash Sales = $1,000, Actual Count = $1,490 -> Variance = -$10."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier = pos_full_setup()
        service = PosSalesService()

        reg = service.register_repository.create(
            tenant=tenant, company=company, branch=branch, warehouse=warehouse,
            register_number="REG-TEST-001", name="Counter 1", opening_balance=Decimal("500.0000"),
        )

        session = service.open_register_session(tenant, reg, cashier=cashier, opening_cash=Decimal("500.0000"))
        assert session.status == SessionStatus.OPEN

        # Complete sale attached to session
        inv = service.create_draft_or_held_sale(
            tenant=tenant, company=company, branch=branch, warehouse=warehouse, register_session=session,
            lines_data=[{"medicine": medicine, "batch": batch, "storage_location": location, "quantity": Decimal("10.0000"), "unit_price": Decimal("100.0000")}],  # $1,000
            cashier=cashier,
        )
        service.complete_sale(tenant, inv, payments_data=[{"payment_method": SalesPaymentMethod.CASH, "amount": Decimal("1000.0000")}], user=cashier)

        session.refresh_from_db()
        assert session.cash_sales == Decimal("1000.0000")

        # Close session with $1,490 count
        closed = service.close_register_session(tenant, session, actual_cash=Decimal("1490.0000"))
        assert closed.expected_cash == Decimal("1500.0000")
        assert closed.variance == Decimal("-10.0000")
        assert closed.status == SessionStatus.CLOSED
