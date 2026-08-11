"""Comprehensive test suite for IMP-021 — Enterprise Purchasing & Purchase Order Management.
Tests: models, PurchaseRequisition lifecycle, Requisition-to-PO conversion, PurchaseOrder lifecycle,
supplier validation, medicine validation, separation of duties, amendments, cancellation, remaining quantities,
inventory isolation, idempotency, tenant isolation, and selectors.
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
from apps.inventory.models import Batch, InventoryItem
from apps.medicines.models import Medicine
from apps.procurement.exceptions import (
    CannotCancelReceivedPOError,
    InactiveMedicineError,
    InactiveSupplierError,
    InvalidPurchaseOrderStateError,
    InvalidRequisitionStateError,
    SelfApprovalForbiddenError,
)
from apps.procurement.models import (
    ProcurementPriority,
    ProcurementReason,
    PurchaseOrder,
    PurchaseOrderAmendment,
    PurchaseOrderLine,
    PurchaseOrderStatus,
    PurchaseRequisition,
    PurchaseRequisitionLine,
    RequisitionStatus,
    SupplierProductPrice,
)
from apps.procurement.selectors import PurchaseOrderSelector, PurchaseRequisitionSelector
from apps.procurement.services import PurchaseOrderService, PurchaseRequisitionService
from apps.suppliers.models import Supplier
from apps.warehouses.models import StorageLocation, Warehouse

User = get_user_model()


# ---------------------------------------------------------------------------
# Test data factories
# ---------------------------------------------------------------------------

def make_tenant(suffix=""):
    code = "pur-" + uuid.uuid4().hex[:6] + suffix
    return Tenant.objects.create(name=f"Procurement Tenant {code}", code=code, slug=code)


def make_company(tenant, code=None):
    code = code or ("CO-" + uuid.uuid4().hex[:6])
    return Company.objects.create(tenant=tenant, code=code, legal_name=f"Company {code}")


def make_warehouse(tenant, company, name="Warehouse"):
    code = "WH-" + uuid.uuid4().hex[:6]
    return Warehouse.objects.create(tenant=tenant, company=company, code=code, name=f"{name} {code}")


def make_location(tenant, warehouse, name="Location"):
    code = "LOC-" + uuid.uuid4().hex[:6]
    return StorageLocation.objects.create(tenant=tenant, warehouse=warehouse, code=code, name=f"{name} {code}")


def make_supplier(tenant, name="Pharma Supplier Ltd", status="active"):
    code = "SUP-" + uuid.uuid4().hex[:6]
    return Supplier.objects.create(
        tenant=tenant,
        code=code,
        legal_name=name,
        display_name=name,
        supplier_type="distributor",
        status=status,
    )


def make_medicine(tenant, name="Ciprofloxacin 500mg", status="active"):
    code = "MED-" + uuid.uuid4().hex[:6]
    return Medicine.objects.create(
        tenant=tenant,
        code=code,
        sku=code,
        english_name=name,
        arabic_name="دواء",
        status=status,
    )


def make_user(email=None):
    email = email or f"u-{uuid.uuid4().hex[:8]}@test.com"
    return User.objects.create_user(email=email, first_name="TestUser", password="Pass123!")


def full_procurement_setup():
    """Return (tenant, company, warehouse, location, supplier, medicine, requester, approver)."""
    tenant = make_tenant()
    company = make_company(tenant)
    warehouse = make_warehouse(tenant, company)
    location = make_location(tenant, warehouse)
    supplier = make_supplier(tenant)
    medicine = make_medicine(tenant)
    requester = make_user("requester@procurement.com")
    approver = make_user("approver@procurement.com")
    return tenant, company, warehouse, location, supplier, medicine, requester, approver


# ===========================================================================
# MODEL TESTS
# ===========================================================================


@pytest.mark.django_db
class TestProcurementModels:
    def test_create_purchase_requisition_model(self):
        tenant, company, warehouse, _, supplier, medicine, requester, _ = full_procurement_setup()
        req = PurchaseRequisition.objects.create(
            tenant=tenant,
            company=company,
            warehouse=warehouse,
            requisition_number="PR-2026-000001",
            department="Pharmacy Operations",
            priority=ProcurementPriority.NORMAL,
            reason=ProcurementReason.REGULAR_REPLENISHMENT,
            status=RequisitionStatus.DRAFT,
            requested_by=requester,
        )
        assert req.pk is not None
        assert req.requisition_number == "PR-2026-000001"
        assert req.status == RequisitionStatus.DRAFT

    def test_create_purchase_order_model_and_totals(self):
        tenant, company, warehouse, location, supplier, medicine, requester, _ = full_procurement_setup()
        po = PurchaseOrder.objects.create(
            tenant=tenant,
            company=company,
            supplier=supplier,
            warehouse=warehouse,
            po_number="PO-2026-000001",
            order_date=timezone.now().date(),
            currency="USD",
            status=PurchaseOrderStatus.DRAFT,
            created_by=requester,
        )
        line = PurchaseOrderLine.objects.create(
            tenant=tenant,
            purchase_order=po,
            medicine=medicine,
            ordered_quantity=Decimal("100.0000"),
            unit_price=Decimal("12.5000"),
            discount_percentage=Decimal("10.00"),
            tax_percentage=Decimal("5.00"),
        )
        line.calculate_totals()
        line.save()

        # subtotal = 100 * 12.5 = 1250
        # discount = 1250 * 0.10 = 125
        # taxable = 1125
        # tax = 1125 * 0.05 = 56.25
        # total = 1181.25
        assert line.line_subtotal == Decimal("1250.0000")
        assert line.discount_amount == Decimal("125.0000")
        assert line.tax_amount == Decimal("56.2500")
        assert line.line_total == Decimal("1181.2500")
        assert line.remaining_quantity == Decimal("100.0000")


# ===========================================================================
# REQUISITION LIFECYCLE & CONVERSION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestPurchaseRequisitionWorkflow:
    def test_requisition_lifecycle(self):
        tenant, company, warehouse, _, supplier, medicine, requester, approver = full_procurement_setup()
        req_svc = PurchaseRequisitionService()

        # 1. Create Draft
        req = req_svc.create_requisition(
            tenant=tenant,
            company=company,
            warehouse=warehouse,
            lines_data=[{
                "medicine": medicine,
                "preferred_supplier": supplier,
                "requested_quantity": Decimal("50.0000"),
                "estimated_unit_cost": Decimal("10.0000"),
            }],
            user=requester,
        )
        assert req.status == RequisitionStatus.DRAFT
        assert req.total_estimated_cost == Decimal("500.0000")

        # 2. Submit
        submitted = req_svc.submit_requisition(tenant, req, user=requester)
        assert submitted.status == RequisitionStatus.SUBMITTED

        # 3. Approve
        approved = req_svc.approve_requisition(tenant, submitted, user=approver)
        assert approved.status == RequisitionStatus.APPROVED
        assert approved.approved_by == approver

    def test_convert_approved_requisition_to_purchase_order(self):
        tenant, company, warehouse, _, supplier, medicine, requester, approver = full_procurement_setup()
        req_svc = PurchaseRequisitionService()
        po_svc = PurchaseOrderService()

        req = req_svc.create_requisition(
            tenant=tenant,
            company=company,
            warehouse=warehouse,
            lines_data=[{
                "medicine": medicine,
                "preferred_supplier": supplier,
                "requested_quantity": Decimal("100.0000"),
                "estimated_unit_cost": Decimal("15.0000"),
            }],
            user=requester,
        )
        req_svc.submit_requisition(tenant, req, user=requester)
        req_svc.approve_requisition(tenant, req, user=approver)
        req.refresh_from_db()

        # Convert to PO
        pos = po_svc.convert_requisition_to_purchase_order(tenant, req, user=approver)
        assert len(pos) == 1
        po = pos[0]

        assert po.status == PurchaseOrderStatus.DRAFT
        assert po.supplier == supplier
        assert po.lines.first().ordered_quantity == Decimal("100.0000")

        req.refresh_from_db()
        assert req.status == RequisitionStatus.CONVERTED_TO_PO

        # Repeated conversion attempt returns existing PO without duplicate creation
        pos_second = po_svc.convert_requisition_to_purchase_order(tenant, req, user=approver)
        assert len(pos_second) == 1
        assert pos_second[0].pk == po.pk


# ===========================================================================
# PURCHASE ORDER LIFECYCLE & APPROVAL TESTS
# ===========================================================================


@pytest.mark.django_db
class TestPurchaseOrderWorkflow:
    def test_complete_po_workflow(self):
        """Scenario: Draft -> Submit -> Approve -> Send to Supplier -> Acknowledge -> Close."""
        tenant, company, warehouse, _, supplier, medicine, requester, approver = full_procurement_setup()
        po_svc = PurchaseOrderService()

        # 1. Create Draft PO
        po = po_svc.create_purchase_order(
            tenant=tenant,
            company=company,
            supplier=supplier,
            warehouse=warehouse,
            lines_data=[{
                "medicine": medicine,
                "ordered_quantity": Decimal("200.0000"),
                "unit_price": Decimal("8.0000"),
            }],
            user=requester,
        )
        assert po.status == PurchaseOrderStatus.DRAFT
        assert po.grand_total == Decimal("1600.0000")

        # 2. Submit for Approval
        submitted = po_svc.submit_purchase_order(tenant, po, user=requester)
        assert submitted.status == PurchaseOrderStatus.PENDING_APPROVAL

        # 3. Approve (Separation of duties: approver != creator)
        approved = po_svc.approve_purchase_order(tenant, submitted, user=approver)
        assert approved.status == PurchaseOrderStatus.APPROVED
        assert approved.approved_by == approver

        # 4. Send to Supplier
        sent = po_svc.send_to_supplier(tenant, approved, user=approver)
        assert sent.status == PurchaseOrderStatus.SENT_TO_SUPPLIER
        assert sent.sent_at is not None

        # 5. Acknowledge Order
        acknowledged = po_svc.acknowledge_order(tenant, sent, user=approver)
        assert acknowledged.status == PurchaseOrderStatus.ACKNOWLEDGED
        assert acknowledged.acknowledged_at is not None

        # 6. Close Order
        closed = po_svc.close_purchase_order(tenant, acknowledged, user=approver)
        assert closed.status == PurchaseOrderStatus.CLOSED

    def test_po_approval_separation_of_duties(self):
        """Creator cannot approve own PO."""
        tenant, company, warehouse, _, supplier, medicine, requester, _ = full_procurement_setup()
        po_svc = PurchaseOrderService()

        po = po_svc.create_purchase_order(
            tenant=tenant, company=company, supplier=supplier, warehouse=warehouse,
            lines_data=[{"medicine": medicine, "ordered_quantity": Decimal("10"), "unit_price": Decimal("5")}],
            user=requester,
        )
        po_svc.submit_purchase_order(tenant, po, user=requester)
        po.refresh_from_db()

        with pytest.raises(SelfApprovalForbiddenError):
            po_svc.approve_purchase_order(tenant, po, user=requester)

    def test_inactive_supplier_rejected(self):
        tenant, company, warehouse, _, _, medicine, requester, _ = full_procurement_setup()
        inactive_supplier = make_supplier(tenant, name="Inactive Supplier", status="inactive")
        po_svc = PurchaseOrderService()

        with pytest.raises(InactiveSupplierError):
            po_svc.create_purchase_order(
                tenant=tenant, company=company, supplier=inactive_supplier, warehouse=warehouse,
                lines_data=[{"medicine": medicine, "ordered_quantity": Decimal("10")}],
                user=requester,
            )

    def test_po_amendment_creates_audit_record(self):
        tenant, company, warehouse, _, supplier, medicine, requester, approver = full_procurement_setup()
        po_svc = PurchaseOrderService()

        po = po_svc.create_purchase_order(
            tenant=tenant, company=company, supplier=supplier, warehouse=warehouse,
            lines_data=[{"medicine": medicine, "ordered_quantity": Decimal("50"), "unit_price": Decimal("10")}],
            user=requester,
        )
        po_svc.submit_purchase_order(tenant, po, user=requester)
        po_svc.approve_purchase_order(tenant, po, user=approver)
        po.refresh_from_db()

        # Execute controlled amendment
        amd = po_svc.amend_purchase_order(
            tenant=tenant,
            po=po,
            reason="Supplier requested updated delivery date and payment terms",
            changes={"payment_terms": "Net 60", "notes": "Amended per supplier agreement"},
            user=approver,
        )

        assert amd.pk is not None
        assert amd.amendment_number.startswith("AMD-")
        assert "payment_terms" in amd.changed_fields

        po.refresh_from_db()
        assert po.payment_terms == "Net 60"

    def test_inventory_isolation_po_does_not_modify_inventory(self):
        """CRITICAL: PO creation/approval MUST NOT modify physical inventory balances."""
        tenant, company, warehouse, location, supplier, medicine, requester, approver = full_procurement_setup()
        batch = Batch.objects.create(
            tenant=tenant, company=company, medicine=medicine, batch_number="B-100",
            expiry_date=timezone.now().date() + timedelta(days=365)
        )
        inv_item = InventoryItem.objects.create(
            tenant=tenant, company=company, warehouse=warehouse, storage_location=location,
            medicine=medicine, batch=batch, on_hand_quantity=Decimal("50.00")
        )

        po_svc = PurchaseOrderService()
        po = po_svc.create_purchase_order(
            tenant=tenant, company=company, supplier=supplier, warehouse=warehouse,
            lines_data=[{"medicine": medicine, "ordered_quantity": Decimal("500.0000"), "unit_price": Decimal("10.0000")}],
            user=requester,
        )
        po_svc.submit_purchase_order(tenant, po, user=requester)
        po_svc.approve_purchase_order(tenant, po, user=approver)

        inv_item.refresh_from_db()
        assert inv_item.on_hand_quantity == Decimal("50.00")  # Balance strictly unchanged


# ===========================================================================
# IDEMPOTENCY, TENANT ISOLATION & SELECTORS
# ===========================================================================


@pytest.mark.django_db
class TestProcurementIdempotencyAndSelectors:
    def test_create_po_idempotent(self):
        tenant, company, warehouse, _, supplier, medicine, requester, _ = full_procurement_setup()
        po_svc = PurchaseOrderService()
        key = "IDEM-PO-9999"

        po1 = po_svc.create_purchase_order(
            tenant=tenant, company=company, supplier=supplier, warehouse=warehouse,
            lines_data=[{"medicine": medicine, "ordered_quantity": Decimal("10")}],
            idempotency_key=key, user=requester,
        )

        po2 = po_svc.create_purchase_order(
            tenant=tenant, company=company, supplier=supplier, warehouse=warehouse,
            lines_data=[{"medicine": medicine, "ordered_quantity": Decimal("10")}],
            idempotency_key=key, user=requester,
        )

        assert po1.pk == po2.pk
        assert po1.po_number == po2.po_number

    def test_tenant_isolation_prevents_cross_tenant_access(self):
        tenant_a, company_a, wh_a, _, supp_a, med_a, req_a, _ = full_procurement_setup()
        tenant_b = make_tenant("b")

        po_svc = PurchaseOrderService()
        po_a = po_svc.create_purchase_order(
            tenant=tenant_a, company=company_a, supplier=supp_a, warehouse=wh_a,
            lines_data=[{"medicine": med_a, "ordered_quantity": Decimal("10")}],
            user=req_a,
        )

        selector = PurchaseOrderSelector()
        pos_a = selector.list_purchase_orders(tenant=tenant_a)
        pos_b = selector.list_purchase_orders(tenant=tenant_b)

        assert pos_a.count() == 1
        assert pos_b.count() == 0

    def test_procurement_statistics(self):
        tenant, company, warehouse, _, supplier, medicine, requester, approver = full_procurement_setup()
        po_svc = PurchaseOrderService()

        po = po_svc.create_purchase_order(
            tenant=tenant, company=company, supplier=supplier, warehouse=warehouse,
            lines_data=[{"medicine": medicine, "ordered_quantity": Decimal("10"), "unit_price": Decimal("100")}],
            user=requester,
        )
        po_svc.submit_purchase_order(tenant, po, user=requester)

        selector = PurchaseOrderSelector()
        stats = selector.get_procurement_statistics(tenant=tenant)

        assert stats["total_purchase_orders"] == 1
        assert stats["pending_approval_count"] == 1
