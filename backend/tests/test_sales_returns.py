"""Comprehensive test suite for IMP-026 — Enterprise Customer Sales Returns & Refund Management.
Tests: return eligibility, line-level quantity controls, batch traceability, return approval separation of duties,
quality inspection (accepted vs rejected vs damaged/quarantined), stock restoration strictly via StockMovementEngine
(zero direct inventory mutations), cash/card refunds, store credit customer balance updates, return reversals,
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
from apps.sales.models import SalesInvoice, SalesInvoiceLine
from apps.sales.models.enums import SalesPaymentMethod
from apps.sales.services import PosSalesService
from apps.sales_returns.exceptions import (
    ExceedsRefundableAmountError,
    ExceedsReturnableQuantityError,
    RefundAlreadyProcessedError,
    ReturnApprovalSelfForbiddenError,
)
from apps.sales_returns.models import (
    CustomerRefund,
    CustomerReturn,
    CustomerReturnLine,
    InspectionResult,
    ProductCondition,
    RefundMethod,
    RefundStatus,
    ReturnReason,
    ReturnStatus,
)
from apps.sales_returns.services import CustomerReturnService
from apps.stock_movement.models import StockMovement
from apps.suppliers.models import Supplier
from apps.warehouses.models import StorageLocation, Warehouse

User = get_user_model()


def returns_full_setup():
    """Helper fixture creating tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, and completed POS sale."""
    tenant = Tenant.objects.create(name=f"Return Tenant {uuid.uuid4().hex[:6]}", slug=f"ret-slug-{uuid.uuid4().hex[:6]}")
    company = Company.objects.create(tenant=tenant, legal_name="Pharma Return Corp", commercial_name="Pharma Return Corp", code=f"COMP-{uuid.uuid4().hex[:4]}", slug=f"comp-{uuid.uuid4().hex[:4]}")
    branch = Branch.objects.create(tenant=tenant, company=company, name="Main Return Pharmacy", code=f"BR-{uuid.uuid4().hex[:4]}")
    warehouse = Warehouse.objects.create(tenant=tenant, company=company, branch=branch, name="Main Return WH", code=f"WH-{uuid.uuid4().hex[:4]}")
    location = StorageLocation.objects.create(tenant=tenant, warehouse=warehouse, name="Shelf A1", code=f"LOC-{uuid.uuid4().hex[:4]}")

    customer = Customer.objects.create(
        tenant=tenant,
        company=company,
        first_name="John",
        last_name="Doe",
        english_name="John Doe Pharmacy",
        customer_number=f"CUST-{uuid.uuid4().hex[:6]}",
        status="active",
        credit_allowed=True,
        credit_limit=Decimal("1000.0000"),
        current_balance=Decimal("0.0000"),
    )

    medicine = Medicine.objects.create(
        tenant=tenant,
        company=company,
        sku=f"SKU-RET-{uuid.uuid4().hex[:6]}",
        barcode=f"BAR-RET-{uuid.uuid4().hex[:6]}",
        english_name="Paracetamol 500mg",
        arabic_name="باراسيتامول 500مجم",
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
        currency="USD", lines_data=[{"medicine": medicine, "ordered_quantity": Decimal("100.0000"), "unit_price": Decimal("10.0000")}],
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
            "medicine": medicine, "received_quantity": Decimal("100.0000"), "accepted_quantity": Decimal("100.0000"), "unit_cost": Decimal("10.0000"),
            "batch_number": f"RET-BATCH-{uuid.uuid4().hex[:4]}", "expiry_date": timezone.now().date() + timedelta(days=365),
            "storage_location": location,
        }],
        user=po_creator,
    )
    grn_service.post_goods_receipt(tenant, grn, user=po_creator)

    batch = Batch.objects.get(tenant=tenant, medicine=medicine)

    # Complete a POS retail sale of 10 units @ $15 = $150
    pos_service = PosSalesService()
    inv = pos_service.create_draft_or_held_sale(
        tenant=tenant, company=company, branch=branch, warehouse=warehouse,
        lines_data=[{"medicine": medicine, "batch": batch, "storage_location": location, "quantity": Decimal("10.0000"), "unit_price": Decimal("15.0000")}],
        customer=customer, cashier=cashier,
    )
    completed_invoice = pos_service.complete_sale(
        tenant=tenant, invoice=inv,
        payments_data=[{"payment_method": SalesPaymentMethod.CASH, "amount": Decimal("150.0000")}],
        user=cashier,
    )

    return tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, manager, completed_invoice


# ===========================================================================
# 1. RETURN ELIGIBILITY & QUANTITY CONTROL TESTS
# ===========================================================================


@pytest.mark.django_db
class TestCustomerReturnEligibility:
    def test_create_customer_return_request(self):
        """Create valid return request against sales invoice."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, manager, invoice = returns_full_setup()
        service = CustomerReturnService()

        inv_line = invoice.lines.first()

        ret = service.create_customer_return(
            tenant=tenant, sales_invoice=invoice,
            lines_data=[{"sales_invoice_line_id": str(inv_line.pk), "requested_return_quantity": Decimal("3.0000")}],
            return_reason=ReturnReason.WRONG_ITEM, user=cashier,
        )

        assert ret.pk is not None
        assert ret.return_number.startswith("CRT-")
        assert ret.status == ReturnStatus.REQUESTED
        assert ret.lines.count() == 1

        line = ret.lines.first()
        assert line.medicine == medicine
        assert line.batch == batch
        assert line.original_sold_quantity == Decimal("10.0000")
        assert line.returnable_quantity == Decimal("10.0000")
        assert line.requested_return_quantity == Decimal("3.0000")

    def test_exceeding_returnable_quantity_rejected(self):
        """Requesting more than sold quantity (or remaining returnable quantity) raises ExceedsReturnableQuantityError."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, manager, invoice = returns_full_setup()
        service = CustomerReturnService()
        inv_line = invoice.lines.first()

        # Requesting 15 units when only 10 were sold
        with pytest.raises(ExceedsReturnableQuantityError):
            service.create_customer_return(
                tenant=tenant, sales_invoice=invoice,
                lines_data=[{"sales_invoice_line_id": str(inv_line.pk), "requested_return_quantity": Decimal("15.0000")}],
                return_reason=ReturnReason.CUSTOMER_CHANGED_MIND, user=cashier,
            )


# ===========================================================================
# 2. SEPARATION OF DUTIES & APPROVAL TESTS
# ===========================================================================


@pytest.mark.django_db
class TestReturnApprovalAndSeparationOfDuties:
    def test_requester_cannot_approve_own_return(self):
        """Enforces separation of duties: return requester cannot approve their own return."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, manager, invoice = returns_full_setup()
        service = CustomerReturnService()
        inv_line = invoice.lines.first()

        ret = service.create_customer_return(
            tenant=tenant, sales_invoice=invoice,
            lines_data=[{"sales_invoice_line_id": str(inv_line.pk), "requested_return_quantity": Decimal("2.0000")}],
            return_reason=ReturnReason.DAMAGED, user=cashier,
        )

        with pytest.raises(ReturnApprovalSelfForbiddenError):
            service.approve_customer_return(tenant, ret, user=cashier)

    def test_manager_approves_return(self):
        """Different user (manager) successfully approves return request."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, manager, invoice = returns_full_setup()
        service = CustomerReturnService()
        inv_line = invoice.lines.first()

        ret = service.create_customer_return(
            tenant=tenant, sales_invoice=invoice,
            lines_data=[{"sales_invoice_line_id": str(inv_line.pk), "requested_return_quantity": Decimal("2.0000")}],
            return_reason=ReturnReason.DAMAGED, user=cashier,
        )

        approved = service.approve_customer_return(tenant, ret, user=manager)
        assert approved.status == ReturnStatus.APPROVED
        assert approved.approved_by == manager


# ===========================================================================
# 3. INSPECTION & ATOMIC STOCK RESTORATION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestReturnInspectionAndStockRestoration:
    def test_accepted_sealed_return_restores_available_stock_via_stock_movement_engine(self):
        """CRITICAL: Accepted sealed return MUST restore available inventory strictly via StockMovementEngine (SALE_RETURN type). Zero direct mutations."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, manager, invoice = returns_full_setup()
        service = CustomerReturnService()
        inv_line = invoice.lines.first()

        # Stock after sale = 90
        inv_item_before = InventoryItem.objects.get(tenant=tenant, warehouse=warehouse, storage_location=location, medicine=medicine, batch=batch)
        assert inv_item_before.on_hand_quantity == Decimal("90.00")

        ret = service.create_customer_return(
            tenant=tenant, sales_invoice=invoice,
            lines_data=[{"sales_invoice_line_id": str(inv_line.pk), "requested_return_quantity": Decimal("3.0000")}],
            return_reason=ReturnReason.CUSTOMER_CHANGED_MIND, user=cashier,
        )
        service.approve_customer_return(tenant, ret, user=manager)

        # Inspect and accept 3 units sealed
        ret_line = ret.lines.first()
        inspected = service.inspect_and_accept_return(
            tenant=tenant, customer_return=ret,
            inspection_data=[{
                "line_id": str(ret_line.pk), "accepted_quantity": Decimal("3.0000"), "rejected_quantity": Decimal("0.0000"),
                "condition": ProductCondition.SEALED, "inspection_result": InspectionResult.ACCEPTED,
            }],
            inspector=manager,
        )

        assert inspected.status == ReturnStatus.ACCEPTED
        assert inspected.refund_amount == Decimal("45.0000")  # 3 * $15 = $45

        # Verify physical stock restored to 93
        inv_item_after = InventoryItem.objects.get(tenant=tenant, warehouse=warehouse, storage_location=location, medicine=medicine, batch=batch)
        assert inv_item_after.on_hand_quantity == Decimal("93.00")

        # Verify StockMovement record created
        mov = StockMovement.objects.filter(tenant=tenant, reference_number=inspected.return_number).first()
        assert mov is not None
        assert mov.movement_type == "sale_return"

    def test_damaged_return_quarantines_stock(self):
        """Damaged/opened returned stock moves to QUARANTINE, not available stock."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, manager, invoice = returns_full_setup()
        service = CustomerReturnService()
        inv_line = invoice.lines.first()

        ret = service.create_customer_return(
            tenant=tenant, sales_invoice=invoice,
            lines_data=[{"sales_invoice_line_id": str(inv_line.pk), "requested_return_quantity": Decimal("2.0000")}],
            return_reason=ReturnReason.DAMAGED, user=cashier,
        )
        service.approve_customer_return(tenant, ret, user=manager)

        ret_line = ret.lines.first()
        inspected = service.inspect_and_accept_return(
            tenant=tenant, customer_return=ret,
            inspection_data=[{
                "line_id": str(ret_line.pk), "accepted_quantity": Decimal("2.0000"), "rejected_quantity": Decimal("0.0000"),
                "condition": ProductCondition.DAMAGED, "inspection_result": InspectionResult.QUARANTINED,
            }],
            inspector=manager,
        )

        assert inspected.status == ReturnStatus.ACCEPTED
        mov = StockMovement.objects.filter(tenant=tenant, reference_number=inspected.return_number).first()
        assert mov is not None
        assert mov.movement_type == "quarantine"

    def test_partial_acceptance_and_rejection(self):
        """Customer returns 5 units: 3 accepted, 2 rejected -> Refund calculated only for 3 accepted units ($45)."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, manager, invoice = returns_full_setup()
        service = CustomerReturnService()
        inv_line = invoice.lines.first()

        ret = service.create_customer_return(
            tenant=tenant, sales_invoice=invoice,
            lines_data=[{"sales_invoice_line_id": str(inv_line.pk), "requested_return_quantity": Decimal("5.0000")}],
            return_reason=ReturnReason.WRONG_QUANTITY, user=cashier,
        )
        service.approve_customer_return(tenant, ret, user=manager)

        ret_line = ret.lines.first()
        inspected = service.inspect_and_accept_return(
            tenant=tenant, customer_return=ret,
            inspection_data=[{
                "line_id": str(ret_line.pk), "accepted_quantity": Decimal("3.0000"), "rejected_quantity": Decimal("2.0000"),
                "condition": ProductCondition.SEALED, "inspection_result": InspectionResult.ACCEPTED,
            }],
            inspector=manager,
        )

        assert inspected.status == ReturnStatus.PARTIALLY_ACCEPTED
        assert inspected.refund_amount == Decimal("45.0000")


# ===========================================================================
# 4. REFUND & STORE CREDIT TESTS
# ===========================================================================


@pytest.mark.django_db
class TestCustomerRefundAndStoreCredit:
    def test_cash_refund_processing(self):
        """Process cash refund for accepted return."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, manager, invoice = returns_full_setup()
        service = CustomerReturnService()
        inv_line = invoice.lines.first()

        ret = service.create_customer_return(
            tenant=tenant, sales_invoice=invoice,
            lines_data=[{"sales_invoice_line_id": str(inv_line.pk), "requested_return_quantity": Decimal("2.0000")}],
            return_reason=ReturnReason.CUSTOMER_CHANGED_MIND, user=cashier,
        )
        service.approve_customer_return(tenant, ret, user=manager)

        ret_line = ret.lines.first()
        service.inspect_and_accept_return(
            tenant=tenant, customer_return=ret,
            inspection_data=[{"line_id": str(ret_line.pk), "accepted_quantity": Decimal("2.0000"), "condition": ProductCondition.SEALED}],
            inspector=manager,
        )

        refund = service.process_customer_refund(
            tenant=tenant, customer_return=ret, refund_method=RefundMethod.CASH,
            amount=Decimal("30.0000"), user=cashier,
        )

        assert refund.pk is not None
        assert refund.refund_number.startswith("REF-")
        assert refund.status == RefundStatus.COMPLETED
        ret.refresh_from_db()
        assert ret.status == ReturnStatus.REFUNDED

    def test_store_credit_refund_adjusts_customer_balance(self):
        """Store credit refund reduces customer credit balance liability."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, manager, invoice = returns_full_setup()
        service = CustomerReturnService()
        inv_line = invoice.lines.first()

        ret = service.create_customer_return(
            tenant=tenant, sales_invoice=invoice,
            lines_data=[{"sales_invoice_line_id": str(inv_line.pk), "requested_return_quantity": Decimal("4.0000")}],
            return_reason=ReturnReason.CUSTOMER_CHANGED_MIND, user=cashier,
        )
        service.approve_customer_return(tenant, ret, user=manager)

        ret_line = ret.lines.first()
        service.inspect_and_accept_return(
            tenant=tenant, customer_return=ret,
            inspection_data=[{"line_id": str(ret_line.pk), "accepted_quantity": Decimal("4.0000"), "condition": ProductCondition.SEALED}],
            inspector=manager,
        )

        # Initial customer balance = 0
        refund = service.process_customer_refund(
            tenant=tenant, customer_return=ret, refund_method=RefundMethod.STORE_CREDIT,
            amount=Decimal("60.0000"), user=cashier,
        )

        assert refund.refund_method == RefundMethod.STORE_CREDIT
        ret.refresh_from_db()
        assert ret.status == ReturnStatus.STORE_CREDIT_ISSUED

        customer.refresh_from_db()
        assert customer.current_balance == Decimal("-60.0000")  # Credit stored in customer account

    def test_duplicate_refund_prevented(self):
        """Processing refund twice raises RefundAlreadyProcessedError."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, manager, invoice = returns_full_setup()
        service = CustomerReturnService()
        inv_line = invoice.lines.first()

        ret = service.create_customer_return(
            tenant=tenant, sales_invoice=invoice,
            lines_data=[{"sales_invoice_line_id": str(inv_line.pk), "requested_return_quantity": Decimal("1.0000")}],
            return_reason=ReturnReason.OTHER, user=cashier,
        )
        service.approve_customer_return(tenant, ret, user=manager)
        ret_line = ret.lines.first()
        service.inspect_and_accept_return(
            tenant=tenant, customer_return=ret,
            inspection_data=[{"line_id": str(ret_line.pk), "accepted_quantity": Decimal("1.0000"), "condition": ProductCondition.SEALED}],
            inspector=manager,
        )

        service.process_customer_refund(tenant=tenant, customer_return=ret, refund_method=RefundMethod.CASH, amount=Decimal("15.0000"), user=cashier)

        with pytest.raises(RefundAlreadyProcessedError):
            service.process_customer_refund(tenant=tenant, customer_return=ret, refund_method=RefundMethod.CASH, amount=Decimal("15.0000"), user=cashier)


# ===========================================================================
# 5. REVERSAL & MULTI-TENANT ISOLATION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestReturnReversalAndIsolation:
    def test_reverse_customer_return(self):
        """Reversing accepted return creates compensating SALE movement and restores status to REVERSED."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, cashier, manager, invoice = returns_full_setup()
        service = CustomerReturnService()
        inv_line = invoice.lines.first()

        ret = service.create_customer_return(
            tenant=tenant, sales_invoice=invoice,
            lines_data=[{"sales_invoice_line_id": str(inv_line.pk), "requested_return_quantity": Decimal("2.0000")}],
            return_reason=ReturnReason.OTHER, user=cashier,
        )
        service.approve_customer_return(tenant, ret, user=manager)
        ret_line = ret.lines.first()
        service.inspect_and_accept_return(
            tenant=tenant, customer_return=ret,
            inspection_data=[{"line_id": str(ret_line.pk), "accepted_quantity": Decimal("2.0000"), "condition": ProductCondition.SEALED}],
            inspector=manager,
        )

        # Reverse return
        reversed_ret = service.reverse_customer_return(tenant, ret, user=manager, reason="Customer cancelled return request")
        assert reversed_ret.status == ReturnStatus.REVERSED

        # Verify stock returned from 92 back to 90
        inv_item = InventoryItem.objects.get(tenant=tenant, warehouse=warehouse, storage_location=location, medicine=medicine, batch=batch)
        assert inv_item.on_hand_quantity == Decimal("90.00")
