"""Comprehensive test suite for IMP-023 — Enterprise Purchase Returns & Supplier Returns.
Tests: models, PurchaseReturn creation, return eligibility validation, quantity limit enforcement,
separation of duties, dispatch engine via StockMovementEngine, supplier acceptance & discrepancy tracking,
credit note generation, reversal workflow, tenant isolation, and selectors.
"""

from __future__ import annotations

import uuid
from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.companies.models import Company
from apps.core.models import Tenant
from apps.goods_receipt.services import GoodsReceiptService
from apps.inventory.models import Batch, InventoryItem
from apps.medicines.models import Medicine
from apps.procurement.services import PurchaseOrderService
from apps.purchase_returns.exceptions import (
    ExceedsReturnableQuantityError,
    InvalidReturnStateError,
    ReturnSelfApprovalForbiddenError,
)
from apps.purchase_returns.models import (
    CreditNoteStatus,
    DiscrepancyStatus,
    ProductCondition,
    PurchaseReturn,
    PurchaseReturnLine,
    ReturnReason,
    ReturnStatus,
)
from apps.purchase_returns.selectors import PurchaseReturnSelector
from apps.purchase_returns.services import PurchaseReturnService
from apps.suppliers.models import Supplier
from apps.warehouses.models import StorageLocation, Warehouse

User = get_user_model()


# ---------------------------------------------------------------------------
# Test data factories
# ---------------------------------------------------------------------------

def make_tenant(suffix=""):
    code = "ret-" + uuid.uuid4().hex[:6] + suffix
    return Tenant.objects.create(name=f"Return Tenant {code}", code=code, slug=code)


def make_company(tenant, code=None):
    code = code or ("CO-" + uuid.uuid4().hex[:6])
    return Company.objects.create(tenant=tenant, code=code, legal_name=f"Company {code}")


def make_warehouse(tenant, company, name="Warehouse"):
    code = "WH-" + uuid.uuid4().hex[:6]
    return Warehouse.objects.create(tenant=tenant, company=company, code=code, name=f"{name} {code}")


def make_location(tenant, warehouse, name="Location"):
    code = "LOC-" + uuid.uuid4().hex[:6]
    return StorageLocation.objects.create(tenant=tenant, warehouse=warehouse, code=code, name=f"{name} {code}")


def make_supplier(tenant, name="Supplier Co Ltd"):
    code = "SUP-" + uuid.uuid4().hex[:6]
    return Supplier.objects.create(
        tenant=tenant,
        code=code,
        legal_name=name,
        display_name=name,
        supplier_type="distributor",
        status="active",
    )


def make_medicine(tenant, name="Amoxicillin 500mg"):
    code = "MED-" + uuid.uuid4().hex[:6]
    return Medicine.objects.create(
        tenant=tenant,
        code=code,
        sku=code,
        english_name=name,
        arabic_name="دواء",
        status="active",
    )


def make_user(email=None):
    email = email or f"u-{uuid.uuid4().hex[:8]}@test.com"
    return User.objects.create_user(email=email, first_name="ReturnUser", password="Pass123!")


def full_return_setup():
    """Setup received inventory via PO & GoodsReceipt posting to provide legitimate stock balance."""
    tenant = make_tenant()
    company = make_company(tenant)
    warehouse = make_warehouse(tenant, company)
    location = make_location(tenant, warehouse)
    supplier = make_supplier(tenant)
    medicine = make_medicine(tenant)
    requester = make_user("requester@returns.com")
    approver = make_user("approver@returns.com")

    # 1. Purchase Order
    po_svc = PurchaseOrderService()
    po = po_svc.create_purchase_order(
        tenant=tenant,
        company=company,
        supplier=supplier,
        warehouse=warehouse,
        lines_data=[{"medicine": medicine, "ordered_quantity": Decimal("100.0000"), "unit_price": Decimal("10.0000")}],
        user=requester,
    )
    po_svc.submit_purchase_order(tenant, po, user=requester)
    po_svc.approve_purchase_order(tenant, po, user=approver)
    po_svc.send_to_supplier(tenant, po, user=approver)

    # 2. Goods Receipt Posting (Adds 100 physical stock to inventory via StockMovementEngine)
    grn_svc = GoodsReceiptService()
    exp = timezone.now().date() + timedelta(days=365)
    grn = grn_svc.create_goods_receipt(
        tenant=tenant,
        company=company,
        supplier=supplier,
        warehouse=warehouse,
        purchase_order=po,
        receiving_location=location,
        lines_data=[{
            "purchase_order_line": po.lines.first(),
            "medicine": medicine,
            "batch_number": "BATCH-RET-100",
            "expiry_date": exp,
            "received_quantity": Decimal("100.0000"),
            "accepted_quantity": Decimal("100.0000"),
            "unit_cost": Decimal("10.0000"),
            "storage_location": location,
        }],
        user=requester,
    )
    posted_grn = grn_svc.post_goods_receipt(tenant, grn, user=requester)

    batch = Batch.objects.get(tenant=tenant, medicine=medicine, batch_number="BATCH-RET-100")
    grn_line = posted_grn.lines.first()

    return tenant, company, warehouse, location, supplier, medicine, batch, posted_grn, grn_line, requester, approver


# ===========================================================================
# MODEL & CREATION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestPurchaseReturnCreation:
    def test_create_purchase_return_draft(self):
        tenant, company, warehouse, location, supplier, medicine, batch, grn, grn_line, requester, _ = full_return_setup()
        service = PurchaseReturnService()

        ret = service.create_purchase_return(
            tenant=tenant,
            company=company,
            supplier=supplier,
            warehouse=warehouse,
            goods_receipt=grn,
            lines_data=[{
                "medicine": medicine,
                "batch": batch,
                "goods_receipt_line": grn_line,
                "storage_location": location,
                "requested_return_quantity": Decimal("20.0000"),
                "approved_return_quantity": Decimal("20.0000"),
                "unit_cost": Decimal("10.0000"),
                "return_reason": ReturnReason.DAMAGED,
            }],
            user=requester,
        )

        assert ret.pk is not None
        assert ret.return_number.startswith("PRT-")
        assert ret.status == ReturnStatus.DRAFT
        assert ret.grand_total == Decimal("200.0000")

    def test_exceeding_available_stock_rejected(self):
        tenant, company, warehouse, location, supplier, medicine, batch, grn, grn_line, requester, _ = full_return_setup()
        service = PurchaseReturnService()

        with pytest.raises(ExceedsReturnableQuantityError):
            service.create_purchase_return(
                tenant=tenant,
                company=company,
                supplier=supplier,
                warehouse=warehouse,
                goods_receipt=grn,
                lines_data=[{
                    "medicine": medicine,
                    "batch": batch,
                    "goods_receipt_line": grn_line,
                    "storage_location": location,
                    "requested_return_quantity": Decimal("500.0000"),  # Exceeds 100 available
                }],
                user=requester,
            )


# ===========================================================================
# WORKFLOW, DISPATCH & STOCK MOVEMENT TESTS
# ===========================================================================


@pytest.mark.django_db
class TestPurchaseReturnWorkflowAndDispatch:
    def test_complete_return_dispatch_workflow(self):
        """Scenario: Create Draft -> Request -> Approve -> Dispatch via StockMovementEngine -> Supplier Acceptance.

        Expected:
        - 30 units removed from physical inventory via StockMovementEngine.
        - Physical balance drops from 100 to 70.
        - Supplier accepts 30 units.
        - Supplier Credit Note (CRN) created for $300.00.
        - Status becomes ACCEPTED.
        """
        tenant, company, warehouse, location, supplier, medicine, batch, grn, grn_line, requester, approver = full_return_setup()
        service = PurchaseReturnService()

        # 1. Create Return
        ret = service.create_purchase_return(
            tenant=tenant,
            company=company,
            supplier=supplier,
            warehouse=warehouse,
            goods_receipt=grn,
            lines_data=[{
                "medicine": medicine,
                "batch": batch,
                "goods_receipt_line": grn_line,
                "storage_location": location,
                "requested_return_quantity": Decimal("30.0000"),
                "approved_return_quantity": Decimal("30.0000"),
                "unit_cost": Decimal("10.0000"),
            }],
            user=requester,
        )

        # 2. Request
        requested = service.request_purchase_return(tenant, ret, user=requester)
        assert requested.status == ReturnStatus.PENDING_APPROVAL

        # 3. Approve (Separation of duties check)
        approved = service.approve_purchase_return(tenant, requested, user=approver)
        assert approved.status == ReturnStatus.APPROVED

        # 4. Dispatch (Removes stock via StockMovementEngine)
        dispatched = service.dispatch_purchase_return(tenant, approved, user=approver)
        assert dispatched.status == ReturnStatus.DISPATCHED

        # Verify physical inventory removed via StockMovementEngine
        inv_item = InventoryItem.objects.get(tenant=tenant, warehouse=warehouse, storage_location=location, medicine=medicine)
        assert inv_item.on_hand_quantity == Decimal("70.00")

        # 5. Record Supplier Full Acceptance
        line = dispatched.lines.first()
        accepted = service.record_supplier_acceptance(
            tenant=tenant,
            purchase_return=dispatched,
            line_acceptances=[{
                "line_id": str(line.pk),
                "supplier_accepted_quantity": Decimal("30.0000"),
                "supplier_rejected_quantity": Decimal("0.0000"),
            }],
            user=approver,
        )
        assert accepted.status == ReturnStatus.ACCEPTED
        assert accepted.credit_notes.count() == 1
        assert accepted.credit_notes.first().net_credit_value == Decimal("300.0000")

    def test_return_approval_separation_of_duties(self):
        """Requester cannot approve own return."""
        tenant, company, warehouse, location, supplier, medicine, batch, grn, grn_line, requester, _ = full_return_setup()
        service = PurchaseReturnService()

        ret = service.create_purchase_return(
            tenant=tenant, company=company, supplier=supplier, warehouse=warehouse, goods_receipt=grn,
            lines_data=[{"medicine": medicine, "batch": batch, "storage_location": location, "requested_return_quantity": Decimal("10")}],
            user=requester,
        )
        service.request_purchase_return(tenant, ret, user=requester)

        with pytest.raises(ReturnSelfApprovalForbiddenError):
            service.approve_purchase_return(tenant, ret, user=requester)

    def test_supplier_partial_acceptance_creates_discrepancy(self):
        """Supplier accepts 20 out of 30 dispatched units, creating a 10 unit discrepancy."""
        tenant, company, warehouse, location, supplier, medicine, batch, grn, grn_line, requester, approver = full_return_setup()
        service = PurchaseReturnService()

        ret = service.create_purchase_return(
            tenant=tenant, company=company, supplier=supplier, warehouse=warehouse, goods_receipt=grn,
            lines_data=[{"medicine": medicine, "batch": batch, "storage_location": location, "requested_return_quantity": Decimal("30")}],
            user=requester,
        )
        service.request_purchase_return(tenant, ret, user=requester)
        service.approve_purchase_return(tenant, ret, user=approver)
        service.dispatch_purchase_return(tenant, ret, user=approver)

        line = ret.lines.first()
        res = service.record_supplier_acceptance(
            tenant=tenant,
            purchase_return=ret,
            line_acceptances=[{
                "line_id": str(line.pk),
                "supplier_accepted_quantity": Decimal("20.0000"),
                "supplier_rejected_quantity": Decimal("10.0000"),
            }],
            user=approver,
        )

        assert res.status == ReturnStatus.DISCREPANCY
        assert res.discrepancies.count() == 1
        disc = res.discrepancies.first()
        assert disc.difference == Decimal("10.0000")
        assert disc.status == DiscrepancyStatus.PENDING


# ===========================================================================
# REVERSAL & ISOLATION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestPurchaseReturnReversalAndSelectors:
    def test_reverse_dispatched_return_restores_inventory(self):
        """Reversing a dispatched return calls StockMovementEngine to restore stock balance."""
        tenant, company, warehouse, location, supplier, medicine, batch, grn, grn_line, requester, approver = full_return_setup()
        service = PurchaseReturnService()

        ret = service.create_purchase_return(
            tenant=tenant, company=company, supplier=supplier, warehouse=warehouse, goods_receipt=grn,
            lines_data=[{"medicine": medicine, "batch": batch, "storage_location": location, "requested_return_quantity": Decimal("25.0000")}],
            user=requester,
        )
        service.request_purchase_return(tenant, ret, user=requester)
        service.approve_purchase_return(tenant, ret, user=approver)
        service.dispatch_purchase_return(tenant, ret, user=approver)

        inv_item = InventoryItem.objects.get(tenant=tenant, warehouse=warehouse, storage_location=location, medicine=medicine)
        assert inv_item.on_hand_quantity == Decimal("75.00")

        # Execute Reversal
        reversed_ret = service.reverse_purchase_return(tenant, ret, reason="Wrong return order dispatched", user=approver)
        assert reversed_ret.status == ReturnStatus.REVERSED

        inv_item.refresh_from_db()
        assert inv_item.on_hand_quantity == Decimal("100.00")

    def test_tenant_isolation(self):
        tenant_a, company_a, wh_a, loc_a, supp_a, med_a, batch_a, grn_a, grn_line_a, req_a, _ = full_return_setup()
        tenant_b = make_tenant("b")

        service = PurchaseReturnService()
        service.create_purchase_return(
            tenant=tenant_a, company=company_a, supplier=supp_a, warehouse=wh_a, goods_receipt=grn_a,
            lines_data=[{"medicine": med_a, "batch": batch_a, "storage_location": loc_a, "requested_return_quantity": Decimal("10")}],
            user=req_a,
        )

        selector = PurchaseReturnSelector()
        assert selector.list_purchase_returns(tenant=tenant_a).count() == 1
        assert selector.list_purchase_returns(tenant=tenant_b).count() == 0
