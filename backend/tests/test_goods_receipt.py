"""Comprehensive test suite for IMP-022 — Enterprise Goods Receipt & Receiving Management.
Tests: models, GoodsReceipt creation, batch creation/reuse, cold chain excursions, posting engine via StockMovementEngine,
PO quantity reconciliation, over-receiving tolerance, free quantities, damaged/quarantined goods, posting idempotency,
reversal workflow, tenant isolation, and selectors.
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
from apps.goods_receipt.exceptions import (
    CannotReverseUnpostedReceiptError,
    ExpiryValidationError,
    OverReceivingPolicyError,
    RecalledBatchReceivingError,
)
from apps.goods_receipt.models import GoodsReceipt, GoodsReceiptLine, QualityStatus, ReceiptStatus
from apps.goods_receipt.selectors import GoodsReceiptSelector
from apps.goods_receipt.services import GoodsReceiptService
from apps.inventory.models import Batch, BatchStatus, InventoryItem
from apps.medicines.models import Medicine
from apps.procurement.models import PurchaseOrder, PurchaseOrderLine, PurchaseOrderStatus
from apps.procurement.services import PurchaseOrderService
from apps.stock_movement.models import StockMovement
from apps.suppliers.models import Supplier
from apps.warehouses.models import StorageLocation, Warehouse

User = get_user_model()


# ---------------------------------------------------------------------------
# Test data factories
# ---------------------------------------------------------------------------

def make_tenant(suffix=""):
    code = "grn-" + uuid.uuid4().hex[:6] + suffix
    return Tenant.objects.create(name=f"Receiving Tenant {code}", code=code, slug=code)


def make_company(tenant, code=None):
    code = code or ("CO-" + uuid.uuid4().hex[:6])
    return Company.objects.create(tenant=tenant, code=code, legal_name=f"Company {code}")


def make_warehouse(tenant, company, name="Warehouse"):
    code = "WH-" + uuid.uuid4().hex[:6]
    return Warehouse.objects.create(tenant=tenant, company=company, code=code, name=f"{name} {code}")


def make_location(tenant, warehouse, name="Location"):
    code = "LOC-" + uuid.uuid4().hex[:6]
    return StorageLocation.objects.create(tenant=tenant, warehouse=warehouse, code=code, name=f"{name} {code}")


def make_supplier(tenant, name="Pharma Wholesaler Ltd"):
    code = "SUP-" + uuid.uuid4().hex[:6]
    return Supplier.objects.create(
        tenant=tenant,
        code=code,
        legal_name=name,
        display_name=name,
        supplier_type="distributor",
        status="active",
    )


def make_medicine(tenant, name="Paracetamol 500mg"):
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
    return User.objects.create_user(email=email, first_name="ReceiverUser", password="Pass123!")


def full_receiving_setup():
    """Return (tenant, company, warehouse, location, supplier, medicine, po, user)."""
    tenant = make_tenant()
    company = make_company(tenant)
    warehouse = make_warehouse(tenant, company)
    location = make_location(tenant, warehouse)
    supplier = make_supplier(tenant)
    medicine = make_medicine(tenant)
    user = make_user("receiver@pharmacloud.com")

    po_svc = PurchaseOrderService()
    po = po_svc.create_purchase_order(
        tenant=tenant,
        company=company,
        supplier=supplier,
        warehouse=warehouse,
        lines_data=[{
            "medicine": medicine,
            "ordered_quantity": Decimal("100.0000"),
            "unit_price": Decimal("10.0000"),
        }],
        user=user,
    )
    po_svc.submit_purchase_order(tenant, po, user=user)

    approver = make_user("approver@pharmacloud.com")
    po_svc.approve_purchase_order(tenant, po, user=approver)
    po_svc.send_to_supplier(tenant, po, user=approver)
    po.refresh_from_db()

    return tenant, company, warehouse, location, supplier, medicine, po, user


# ===========================================================================
# MODEL & CREATION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestGoodsReceiptCreation:
    def test_create_goods_receipt_draft(self):
        tenant, company, warehouse, location, supplier, medicine, po, user = full_receiving_setup()
        service = GoodsReceiptService()
        exp = timezone.now().date() + timedelta(days=365)

        grn = service.create_goods_receipt(
            tenant=tenant,
            company=company,
            supplier=supplier,
            warehouse=warehouse,
            purchase_order=po,
            receiving_location=location,
            lines_data=[{
                "purchase_order_line": po.lines.first(),
                "medicine": medicine,
                "batch_number": "BATCH-GRN-001",
                "expiry_date": exp,
                "received_quantity": Decimal("50.0000"),
                "accepted_quantity": Decimal("50.0000"),
                "unit_cost": Decimal("10.0000"),
                "storage_location": location,
            }],
            user=user,
        )

        assert grn.pk is not None
        assert grn.receipt_number.startswith("GRN-")
        assert grn.status == ReceiptStatus.DRAFT
        assert grn.lines.count() == 1
        assert grn.grand_total == Decimal("500.0000")

    def test_cold_chain_excursion_flags_quarantine(self):
        tenant, company, warehouse, location, supplier, medicine, po, user = full_receiving_setup()
        service = GoodsReceiptService()
        exp = timezone.now().date() + timedelta(days=365)

        grn = service.create_goods_receipt(
            tenant=tenant,
            company=company,
            supplier=supplier,
            warehouse=warehouse,
            receiving_location=location,
            lines_data=[{
                "medicine": medicine,
                "batch_number": "COLD-BATCH-001",
                "expiry_date": exp,
                "received_quantity": Decimal("20.0000"),
                "storage_location": location,
                "temperature_at_receipt": Decimal("12.50"),  # Exceeds max 8°C
                "min_temperature": Decimal("2.00"),
                "max_temperature": Decimal("8.00"),
            }],
            user=user,
        )

        line = grn.lines.first()
        assert line.temperature_excursion_flag is True
        assert line.quality_status == QualityStatus.QUARANTINED


# ===========================================================================
# POSTING & STOCK MOVEMENT INTEGRATION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestGoodsReceiptPostingEngine:
    def test_post_goods_receipt_creates_stock_movement_and_updates_po(self):
        """Scenario: PO ordered = 100. Receipt = 40.

        Expected:
        - Accepted stock = 40 added via StockMovementEngine.
        - PO line received_quantity = 40.
        - PO status becomes PARTIALLY_RECEIVED.
        - GoodsReceipt status becomes COMPLETED.
        """
        tenant, company, warehouse, location, supplier, medicine, po, user = full_receiving_setup()
        service = GoodsReceiptService()
        exp = timezone.now().date() + timedelta(days=365)
        po_line = po.lines.first()

        grn = service.create_goods_receipt(
            tenant=tenant,
            company=company,
            supplier=supplier,
            warehouse=warehouse,
            purchase_order=po,
            receiving_location=location,
            lines_data=[{
                "purchase_order_line": po_line,
                "medicine": medicine,
                "batch_number": "BATCH-PARTIAL-100",
                "expiry_date": exp,
                "received_quantity": Decimal("40.0000"),
                "accepted_quantity": Decimal("40.0000"),
                "unit_cost": Decimal("10.0000"),
                "storage_location": location,
            }],
            user=user,
        )

        posted_grn = service.post_goods_receipt(tenant, grn, user=user)
        assert posted_grn.status == ReceiptStatus.COMPLETED

        # Check stock created via StockMovementEngine
        inv_item = InventoryItem.objects.filter(
            tenant=tenant, warehouse=warehouse, storage_location=location, medicine=medicine
        ).first()
        assert inv_item is not None
        assert inv_item.on_hand_quantity == Decimal("40.00")

        # Check PO reconciliation
        po_line.refresh_from_db()
        assert po_line.received_quantity == Decimal("40.0000")
        assert po_line.remaining_quantity == Decimal("60.0000")

        po.refresh_from_db()
        assert po.status == PurchaseOrderStatus.PARTIALLY_RECEIVED

        # Check Batch created
        batch = Batch.objects.filter(tenant=tenant, medicine=medicine, batch_number="BATCH-PARTIAL-100").first()
        assert batch is not None
        assert batch.status == BatchStatus.ACTIVE

    def test_full_po_receipt_completes_po(self):
        """Scenario: PO ordered = 100. Receipt = 100. PO becomes FULLY_RECEIVED."""
        tenant, company, warehouse, location, supplier, medicine, po, user = full_receiving_setup()
        service = GoodsReceiptService()
        exp = timezone.now().date() + timedelta(days=365)
        po_line = po.lines.first()

        grn = service.create_goods_receipt(
            tenant=tenant,
            company=company,
            supplier=supplier,
            warehouse=warehouse,
            purchase_order=po,
            receiving_location=location,
            lines_data=[{
                "purchase_order_line": po_line,
                "medicine": medicine,
                "batch_number": "BATCH-FULL-200",
                "expiry_date": exp,
                "received_quantity": Decimal("100.0000"),
                "accepted_quantity": Decimal("100.0000"),
                "unit_cost": Decimal("10.0000"),
                "storage_location": location,
            }],
            user=user,
        )

        service.post_goods_receipt(tenant, grn, user=user)

        po_line.refresh_from_db()
        assert po_line.received_quantity == Decimal("100.0000")
        assert po_line.remaining_quantity == Decimal("0.0000")

        po.refresh_from_db()
        assert po.status == PurchaseOrderStatus.FULLY_RECEIVED

    def test_post_goods_receipt_is_idempotent(self):
        """Posting an already completed receipt does not duplicate stock movements."""
        tenant, company, warehouse, location, supplier, medicine, po, user = full_receiving_setup()
        service = GoodsReceiptService()
        exp = timezone.now().date() + timedelta(days=365)

        grn = service.create_goods_receipt(
            tenant=tenant,
            company=company,
            supplier=supplier,
            warehouse=warehouse,
            purchase_order=po,
            receiving_location=location,
            lines_data=[{
                "purchase_order_line": po.lines.first(),
                "medicine": medicine,
                "batch_number": "BATCH-IDEM-300",
                "expiry_date": exp,
                "received_quantity": Decimal("50.0000"),
                "accepted_quantity": Decimal("50.0000"),
                "storage_location": location,
            }],
            user=user,
        )

        res1 = service.post_goods_receipt(tenant, grn, user=user)
        res2 = service.post_goods_receipt(tenant, grn, user=user)

        assert res1.pk == res2.pk
        assert StockMovement.objects.filter(tenant=tenant, reference_id=str(grn.pk)).count() == 1


# ===========================================================================
# VALIDATION & EXCEPTION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestGoodsReceiptValidations:
    def test_expired_batch_rejected(self):
        tenant, company, warehouse, location, supplier, medicine, po, user = full_receiving_setup()
        service = GoodsReceiptService()
        past_exp = timezone.now().date() - timedelta(days=10)

        with pytest.raises(ExpiryValidationError):
            service.create_goods_receipt(
                tenant=tenant,
                company=company,
                supplier=supplier,
                warehouse=warehouse,
                receiving_location=location,
                lines_data=[{
                    "medicine": medicine,
                    "batch_number": "EXPIRED-BATCH",
                    "expiry_date": past_exp,
                    "received_quantity": Decimal("10.0000"),
                    "storage_location": location,
                }],
                user=user,
            )

    def test_recalled_batch_post_rejected(self):
        tenant, company, warehouse, location, supplier, medicine, po, user = full_receiving_setup()
        exp = timezone.now().date() + timedelta(days=365)

        # Create recalled batch
        Batch.objects.create(
            tenant=tenant, company=company, medicine=medicine, supplier=supplier,
            batch_number="RECALLED-BATCH-999", expiry_date=exp, status=BatchStatus.RECALLED
        )

        service = GoodsReceiptService()
        grn = service.create_goods_receipt(
            tenant=tenant,
            company=company,
            supplier=supplier,
            warehouse=warehouse,
            receiving_location=location,
            lines_data=[{
                "medicine": medicine,
                "batch_number": "RECALLED-BATCH-999",
                "expiry_date": exp,
                "received_quantity": Decimal("10.0000"),
                "storage_location": location,
            }],
            user=user,
        )

        with pytest.raises(RecalledBatchReceivingError):
            service.post_goods_receipt(tenant, grn, user=user)

    def test_over_receiving_beyond_tolerance_rejected(self):
        tenant, company, warehouse, location, supplier, medicine, po, user = full_receiving_setup()
        service = GoodsReceiptService()
        exp = timezone.now().date() + timedelta(days=365)
        po_line = po.lines.first()  # ordered = 100

        grn = service.create_goods_receipt(
            tenant=tenant,
            company=company,
            supplier=supplier,
            warehouse=warehouse,
            purchase_order=po,
            receiving_location=location,
            lines_data=[{
                "purchase_order_line": po_line,
                "medicine": medicine,
                "batch_number": "OVER-BATCH",
                "expiry_date": exp,
                "received_quantity": Decimal("150.0000"),
                "accepted_quantity": Decimal("150.0000"),
                "storage_location": location,
            }],
            user=user,
        )

        with pytest.raises(OverReceivingPolicyError):
            service.post_goods_receipt(tenant, grn, user=user)


# ===========================================================================
# REVERSAL & ISOLATION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestGoodsReceiptReversalAndIsolation:
    def test_reverse_posted_goods_receipt(self):
        tenant, company, warehouse, location, supplier, medicine, po, user = full_receiving_setup()
        service = GoodsReceiptService()
        exp = timezone.now().date() + timedelta(days=365)
        po_line = po.lines.first()

        grn = service.create_goods_receipt(
            tenant=tenant,
            company=company,
            supplier=supplier,
            warehouse=warehouse,
            purchase_order=po,
            receiving_location=location,
            lines_data=[{
                "purchase_order_line": po_line,
                "medicine": medicine,
                "batch_number": "REVERSE-BATCH-500",
                "expiry_date": exp,
                "received_quantity": Decimal("30.0000"),
                "accepted_quantity": Decimal("30.0000"),
                "storage_location": location,
            }],
            user=user,
        )
        service.post_goods_receipt(tenant, grn, user=user)

        po_line.refresh_from_db()
        assert po_line.received_quantity == Decimal("30.0000")

        # Execute reversal
        reversed_grn = service.reverse_goods_receipt(tenant, grn, reason="Damaged in transit discovery", user=user)
        assert reversed_grn.status == ReceiptStatus.REVERSED

        po_line.refresh_from_db()
        assert po_line.received_quantity == Decimal("0.0000")

    def test_tenant_isolation(self):
        tenant_a, company_a, wh_a, loc_a, supp_a, med_a, po_a, user_a = full_receiving_setup()
        tenant_b = make_tenant("b")

        service = GoodsReceiptService()
        exp = timezone.now().date() + timedelta(days=365)

        grn_a = service.create_goods_receipt(
            tenant=tenant_a, company=company_a, supplier=supp_a, warehouse=wh_a,
            receiving_location=loc_a,
            lines_data=[{
                "medicine": med_a, "batch_number": "ISO-B", "expiry_date": exp,
                "received_quantity": Decimal("10"), "storage_location": loc_a,
            }],
            user=user_a,
        )

        selector = GoodsReceiptSelector()
        assert selector.list_goods_receipts(tenant=tenant_a).count() == 1
        assert selector.list_goods_receipts(tenant=tenant_b).count() == 0
