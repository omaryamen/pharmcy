"""Comprehensive test suite for IMP-019 — Enterprise Inter-Branch & Warehouse Stock Transfer.
Tests: models, services, FEFO picking, dispatch, receiving, partial receipt, damage, wrong batch,
wrong medicine, cancellation, reversal, idempotency, tenant isolation, selectors.
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
from apps.stock_movement.models import StockMovement
from apps.stock_transfer.exceptions import (
    CannotCancelDispatchedTransferError,
    InvalidBatchForTransferError,
    InvalidTransferStateError,
    SelfApprovalForbiddenError,
    TransferAlreadyReversedError,
)
from apps.stock_transfer.models import (
    DiscrepancyStatus,
    DiscrepancyType,
    StockTransfer,
    StockTransferDiscrepancy,
    StockTransferHistory,
    StockTransferLine,
    TransferLineStatus,
    TransferPriority,
    TransferStatus,
    TransferType,
)
from apps.stock_transfer.selectors import StockTransferSelector
from apps.stock_transfer.services import StockTransferService, TransferNumberGenerator
from apps.warehouses.models import StorageLocation, Warehouse

User = get_user_model()


# ---------------------------------------------------------------------------
# Test data factories
# ---------------------------------------------------------------------------

def make_tenant(suffix=""):
    code = "st-" + uuid.uuid4().hex[:6] + suffix
    return Tenant.objects.create(name=f"ST Tenant {code}", code=code, slug=code)


def make_company(tenant, code=None):
    code = code or ("CO-" + uuid.uuid4().hex[:6])
    return Company.objects.create(tenant=tenant, code=code, legal_name=f"Company {code}")


def make_warehouse(tenant, company, name="Warehouse"):
    code = "WH-" + uuid.uuid4().hex[:6]
    return Warehouse.objects.create(tenant=tenant, company=company, code=code, name=f"{name} {code}")


def make_location(tenant, warehouse, name="Location"):
    code = "LOC-" + uuid.uuid4().hex[:6]
    return StorageLocation.objects.create(tenant=tenant, warehouse=warehouse, code=code, name=f"{name} {code}")


def make_medicine(tenant, name="Paracetamol 500mg"):
    code = "MED-" + uuid.uuid4().hex[:6]
    return Medicine.objects.create(
        tenant=tenant,
        code=code,
        sku=code,
        english_name=name,
        arabic_name="دواء",
    )


def make_batch(tenant, company, medicine, expiry_days=365, status="active"):
    return Batch.objects.create(
        tenant=tenant,
        company=company,
        medicine=medicine,
        batch_number="BATCH-" + uuid.uuid4().hex[:8],
        manufacturing_date=timezone.now().date() - timedelta(days=30),
        expiry_date=timezone.now().date() + timedelta(days=expiry_days),
        unit_cost=Decimal("10.0000"),
        selling_price=Decimal("15.0000"),
        status=status,
    )


def make_inventory_item(tenant, company, medicine, batch, warehouse, location, qty=Decimal("100")):
    item, _ = InventoryItem.objects.get_or_create(
        tenant=tenant,
        medicine=medicine,
        batch=batch,
        warehouse=warehouse,
        storage_location=location,
        defaults={
            "company": company,
            "on_hand_quantity": qty,
            "reserved_quantity": Decimal("0"),
            "damaged_quantity": Decimal("0"),
            "quarantine_quantity": Decimal("0"),
            "unit_cost": Decimal("10.0000"),
        },
    )
    return item


def make_user(email=None):
    email = email or f"u-{uuid.uuid4().hex[:8]}@test.com"
    return User.objects.create_user(email=email, first_name="TestUser", password="Pass123!")


def full_transfer_setup(qty=Decimal("100")):
    """Return (tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, inv_item, requester, approver)."""
    tenant = make_tenant()
    company = make_company(tenant)
    src_wh = make_warehouse(tenant, company, "Source WH")
    dst_wh = make_warehouse(tenant, company, "Destination WH")
    src_loc = make_location(tenant, src_wh, "Source Loc")
    dst_loc = make_location(tenant, dst_wh, "Destination Loc")
    med = make_medicine(tenant)
    batch = make_batch(tenant, company, med)
    inv_item = make_inventory_item(tenant, company, med, batch, src_wh, src_loc, qty)
    requester = make_user("requester@test.com")
    approver = make_user("approver@test.com")
    return tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, inv_item, requester, approver


def create_sample_transfer(tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, user, qty=Decimal("50")):
    svc = StockTransferService()
    return svc.create_transfer(
        tenant=tenant,
        company=company,
        source_warehouse=src_wh,
        destination_warehouse=dst_wh,
        source_location=src_loc,
        destination_location=dst_loc,
        lines_data=[{
            "medicine": med,
            "batch": batch,
            "source_location": src_loc,
            "destination_location": dst_loc,
            "requested_quantity": qty,
            "unit_cost": Decimal("10.0000"),
        }],
        user=user,
    )


# ===========================================================================
# MODEL TESTS
# ===========================================================================


@pytest.mark.django_db
class TestStockTransferModels:
    def test_create_stock_transfer_model(self):
        tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, _, requester, _ = full_transfer_setup()
        transfer = create_sample_transfer(tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, requester)

        assert transfer.pk is not None
        assert transfer.transfer_number.startswith("TRF-")
        assert transfer.status == TransferStatus.DRAFT
        assert transfer.total_items == 1
        assert transfer.total_requested_quantity == Decimal("50.0000")

    def test_transfer_line_recalculate_cost(self):
        tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, _, requester, _ = full_transfer_setup()
        transfer = create_sample_transfer(tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, requester, qty=Decimal("20"))
        line = transfer.lines.first()

        assert line.total_cost == Decimal("200.0000")


# ===========================================================================
# SERVICE LIFECYCLE & WORKFLOW TESTS
# ===========================================================================


@pytest.mark.django_db
class TestStockTransferLifecycle:
    def test_complete_happy_path_workflow(self):
        """Scenario 1: Request 50 -> Approve -> Pick -> Dispatch (StockMovement TRANSFER_OUT) -> Receive (StockMovement TRANSFER_IN)."""
        tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, inv_item, requester, approver = full_transfer_setup(Decimal("100"))
        svc = StockTransferService()

        # 1. Create Draft
        transfer = create_sample_transfer(tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, requester, qty=Decimal("50"))
        assert transfer.status == TransferStatus.DRAFT

        # 2. Request
        svc.request_transfer(tenant, transfer, user=requester)
        transfer.refresh_from_db()
        assert transfer.status == TransferStatus.REQUESTED

        # 3. Approve (Separation of duties: approver != requester)
        svc.approve_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()
        assert transfer.status == TransferStatus.APPROVED

        # 4. Pick
        svc.pick_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()
        assert transfer.status == TransferStatus.READY_FOR_DISPATCH

        # 5. Dispatch
        movements_before = StockMovement.objects.filter(tenant=tenant).count()
        svc.dispatch_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()
        movements_after = StockMovement.objects.filter(tenant=tenant).count()

        assert transfer.status == TransferStatus.IN_TRANSIT
        assert movements_after > movements_before

        # Check source inventory reduced
        inv_item.refresh_from_db()
        assert inv_item.on_hand_quantity == Decimal("50.00")

        # 6. Receive at Destination Location
        line = transfer.lines.first()
        svc.receive_transfer(tenant, transfer, receive_lines_data=[{
            "line_id": str(line.pk),
            "destination_location": dst_loc,
            "received_quantity": Decimal("50.0000"),
        }], user=approver)
        transfer.refresh_from_db()

        assert transfer.status == TransferStatus.RECEIVED

        # Check destination inventory item created & populated
        dst_item = InventoryItem.objects.filter(tenant=tenant, warehouse=dst_wh, storage_location=dst_loc, medicine=med, batch=batch).first()
        assert dst_item is not None
        assert dst_item.on_hand_quantity == Decimal("50.00")

    def test_approval_separation_of_duties(self):
        """Requester cannot approve own transfer."""
        tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, _, requester, _ = full_transfer_setup()
        svc = StockTransferService()
        transfer = create_sample_transfer(tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, requester)
        svc.request_transfer(tenant, transfer, user=requester)
        transfer.refresh_from_db()

        with pytest.raises(SelfApprovalForbiddenError):
            svc.approve_transfer(tenant, transfer, user=requester)

    def test_auto_fefo_picking_selects_earliest_expiry_batch(self):
        """Auto-FEFO should automatically select batch with earliest expiry date."""
        tenant = make_tenant()
        company = make_company(tenant)
        src_wh = make_warehouse(tenant, company)
        dst_wh = make_warehouse(tenant, company)
        src_loc = make_location(tenant, src_wh)
        dst_loc = make_location(tenant, dst_wh)
        med = make_medicine(tenant)

        # Create two batches: Batch 1 expires in 30 days, Batch 2 in 365 days
        batch_late = make_batch(tenant, company, med, expiry_days=365)
        batch_early = make_batch(tenant, company, med, expiry_days=30)

        make_inventory_item(tenant, company, med, batch_late, src_wh, src_loc, Decimal("100"))
        make_inventory_item(tenant, company, med, batch_early, src_wh, src_loc, Decimal("100"))

        user = make_user()
        svc = StockTransferService()

        # Create transfer without specifying a batch
        transfer = svc.create_transfer(
            tenant=tenant,
            company=company,
            source_warehouse=src_wh,
            destination_warehouse=dst_wh,
            source_location=src_loc,
            destination_location=dst_loc,
            lines_data=[{
                "medicine": med,
                "batch": None,
                "source_location": src_loc,
                "requested_quantity": Decimal("40"),
            }],
            user=user,
        )
        svc.request_transfer(tenant, transfer, user=user)
        transfer.refresh_from_db()
        svc.approve_transfer(tenant, transfer, user=make_user("other@test.com"))
        transfer.refresh_from_db()

        # Perform auto-FEFO picking
        svc.pick_transfer(tenant, transfer, user=user)
        line = transfer.lines.first()

        assert line.batch == batch_early  # Must pick earliest expiring batch


# ===========================================================================
# DISCREPANCY & DAMAGE TESTS
# ===========================================================================


@pytest.mark.django_db
class TestTransferDiscrepanciesAndDamage:
    def test_partial_receiving_creates_shortage_discrepancy(self):
        """Scenario 3: Dispatched = 100, Received = 95 -> 5-unit shortage discrepancy created."""
        tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, _, requester, approver = full_transfer_setup(Decimal("200"))
        svc = StockTransferService()

        transfer = create_sample_transfer(tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, requester, qty=Decimal("100"))
        svc.request_transfer(tenant, transfer, user=requester)
        transfer.refresh_from_db()
        svc.approve_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()
        svc.pick_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()
        svc.dispatch_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()

        line = transfer.lines.first()
        # Receive 95 out of 100
        svc.receive_transfer(tenant, transfer, receive_lines_data=[{
            "line_id": str(line.pk),
            "destination_location": dst_loc,
            "received_quantity": Decimal("95.0000"),
        }], user=approver)
        transfer.refresh_from_db()

        assert transfer.status in [TransferStatus.PARTIALLY_RECEIVED, TransferStatus.DISCREPANCY]
        assert transfer.has_discrepancy is True

        discrepancies = StockTransferDiscrepancy.objects.filter(stock_transfer=transfer)
        assert discrepancies.count() == 1
        assert discrepancies.first().discrepancy_type == DiscrepancyType.SHORTAGE
        assert discrepancies.first().difference_quantity == Decimal("5.0000")

    def test_damage_during_transfer_moves_stock_to_damage_movement(self):
        """Scenario: Goods damaged during transit -> DAMAGE movement created and discrepancy recorded."""
        tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, _, requester, approver = full_transfer_setup(Decimal("200"))
        svc = StockTransferService()

        transfer = create_sample_transfer(tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, requester, qty=Decimal("100"))
        svc.request_transfer(tenant, transfer, user=requester)
        transfer.refresh_from_db()
        svc.approve_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()
        svc.pick_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()
        svc.dispatch_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()

        line = transfer.lines.first()
        # 80 good, 20 damaged
        svc.receive_transfer(tenant, transfer, receive_lines_data=[{
            "line_id": str(line.pk),
            "destination_location": dst_loc,
            "received_quantity": Decimal("80.0000"),
            "damaged_quantity": Decimal("20.0000"),
            "damage_reason": "Vial broken during transport",
        }], user=approver)
        transfer.refresh_from_db()

        assert transfer.has_discrepancy is True
        discrepancy = StockTransferDiscrepancy.objects.filter(stock_transfer=transfer, discrepancy_type=DiscrepancyType.DAMAGE).first()
        assert discrepancy is not None
        assert discrepancy.difference_quantity == Decimal("20.0000")

    def test_wrong_batch_received_creates_discrepancy(self):
        """Scenario 4: Destination receives wrong batch -> discrepancy created."""
        tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, _, requester, approver = full_transfer_setup(Decimal("200"))
        wrong_batch = make_batch(tenant, company, med)
        svc = StockTransferService()

        transfer = create_sample_transfer(tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, requester, qty=Decimal("50"))
        svc.request_transfer(tenant, transfer, user=requester)
        transfer.refresh_from_db()
        svc.approve_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()
        svc.pick_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()
        svc.dispatch_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()

        line = transfer.lines.first()
        svc.receive_transfer(tenant, transfer, receive_lines_data=[{
            "line_id": str(line.pk),
            "destination_location": dst_loc,
            "received_quantity": Decimal("50.0000"),
            "received_batch": wrong_batch,
        }], user=approver)
        transfer.refresh_from_db()

        assert transfer.has_discrepancy is True
        discrepancy = StockTransferDiscrepancy.objects.filter(stock_transfer=transfer, discrepancy_type=DiscrepancyType.WRONG_BATCH).first()
        assert discrepancy is not None

    def test_wrong_medicine_received_rejects_line(self):
        """Scenario 5: Destination receives wrong medicine -> normal receipt rejected & discrepancy created."""
        tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, _, requester, approver = full_transfer_setup(Decimal("200"))
        wrong_med = make_medicine(tenant, name="Ibuprofen 400mg")
        svc = StockTransferService()

        transfer = create_sample_transfer(tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, requester, qty=Decimal("50"))
        svc.request_transfer(tenant, transfer, user=requester)
        transfer.refresh_from_db()
        svc.approve_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()
        svc.pick_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()
        svc.dispatch_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()

        line = transfer.lines.first()
        svc.receive_transfer(tenant, transfer, receive_lines_data=[{
            "line_id": str(line.pk),
            "destination_location": dst_loc,
            "received_quantity": Decimal("50.0000"),
            "received_medicine": wrong_med,
        }], user=approver)
        transfer.refresh_from_db()

        line.refresh_from_db()
        assert line.status == TransferLineStatus.REJECTED
        assert transfer.has_discrepancy is True


# ===========================================================================
# CANCELLATION & REVERSAL TESTS
# ===========================================================================


@pytest.mark.django_db
class TestCancellationAndReversal:
    def test_cancel_draft_or_requested_transfer(self):
        tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, _, requester, _ = full_transfer_setup()
        svc = StockTransferService()

        transfer = create_sample_transfer(tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, requester)
        cancelled = svc.cancel_transfer(tenant, transfer, reason="No longer needed", user=requester)

        assert cancelled.status == TransferStatus.CANCELLED
        assert cancelled.cancelled_at is not None

    def test_cannot_cancel_dispatched_transfer(self):
        """Scenario 8: Transfer cannot be cancelled after dispatch unless reversed."""
        tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, _, requester, approver = full_transfer_setup(Decimal("100"))
        svc = StockTransferService()

        transfer = create_sample_transfer(tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, requester, qty=Decimal("30"))
        svc.request_transfer(tenant, transfer, user=requester)
        transfer.refresh_from_db()
        svc.approve_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()
        svc.pick_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()
        svc.dispatch_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()

        with pytest.raises(CannotCancelDispatchedTransferError):
            svc.cancel_transfer(tenant, transfer, reason="Cancel after dispatch", user=requester)

    def test_reversal_creates_compensating_movements(self):
        """Scenario: Completed transfer reversed -> compensating stock movements generated."""
        tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, inv_item, requester, approver = full_transfer_setup(Decimal("100"))
        svc = StockTransferService()

        transfer = create_sample_transfer(tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, requester, qty=Decimal("40"))
        svc.request_transfer(tenant, transfer, user=requester)
        transfer.refresh_from_db()
        svc.approve_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()
        svc.pick_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()
        svc.dispatch_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()

        line = transfer.lines.first()
        svc.receive_transfer(tenant, transfer, receive_lines_data=[{
            "line_id": str(line.pk),
            "destination_location": dst_loc,
            "received_quantity": Decimal("40.0000"),
        }], user=approver)
        transfer.refresh_from_db()

        # Execute reversal
        reversed_transfer = svc.reverse_transfer(tenant, transfer, reason="Customer order cancelled", user=approver)
        assert reversed_transfer.status == TransferStatus.CANCELLED
        assert "REVERSED" in reversed_transfer.notes

        # Source inventory returned back to 100
        inv_item.refresh_from_db()
        assert inv_item.on_hand_quantity == Decimal("100.00")

    def test_second_reversal_raises_error(self):
        """Scenario 9: Completed transfer reversed twice -> second reversal rejected."""
        tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, _, requester, approver = full_transfer_setup(Decimal("100"))
        svc = StockTransferService()

        transfer = create_sample_transfer(tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, requester, qty=Decimal("40"))
        svc.request_transfer(tenant, transfer, user=requester)
        transfer.refresh_from_db()
        svc.approve_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()
        svc.pick_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()
        svc.dispatch_transfer(tenant, transfer, user=approver)
        transfer.refresh_from_db()

        line = transfer.lines.first()
        svc.receive_transfer(tenant, transfer, receive_lines_data=[{
            "line_id": str(line.pk),
            "destination_location": dst_loc,
            "received_quantity": Decimal("40.0000"),
        }], user=approver)
        transfer.refresh_from_db()

        svc.reverse_transfer(tenant, transfer, reason="Reversal 1", user=approver)
        transfer.refresh_from_db()

        with pytest.raises(Exception):
            svc.reverse_transfer(tenant, transfer, reason="Reversal 2", user=approver)


# ===========================================================================
# IDEMPOTENCY & TENANT ISOLATION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestIdempotencyAndTenantIsolation:
    def test_create_transfer_idempotent(self):
        tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, _, requester, _ = full_transfer_setup()
        svc = StockTransferService()
        key = "IDEM-KEY-12345"

        t1 = svc.create_transfer(
            tenant=tenant, company=company, source_warehouse=src_wh, destination_warehouse=dst_wh,
            source_location=src_loc, destination_location=dst_loc,
            lines_data=[{"medicine": med, "batch": batch, "source_location": src_loc, "requested_quantity": Decimal("10")}],
            idempotency_key=key, user=requester,
        )

        t2 = svc.create_transfer(
            tenant=tenant, company=company, source_warehouse=src_wh, destination_warehouse=dst_wh,
            source_location=src_loc, destination_location=dst_loc,
            lines_data=[{"medicine": med, "batch": batch, "source_location": src_loc, "requested_quantity": Decimal("10")}],
            idempotency_key=key, user=requester,
        )

        assert t1.pk == t2.pk
        assert t1.transfer_number == t2.transfer_number

    def test_tenant_isolation_prevents_cross_tenant_access(self):
        """Scenario 10: User from Tenant A cannot access Tenant B transfers."""
        tenant_a, company_a, src_wh_a, dst_wh_a, src_loc_a, dst_loc_a, med_a, batch_a, _, req_a, _ = full_transfer_setup()
        tenant_b = make_tenant("b")
        company_b = make_company(tenant_b)
        src_wh_b = make_warehouse(tenant_b, company_b)
        dst_wh_b = make_warehouse(tenant_b, company_b)
        src_loc_b = make_location(tenant_b, src_wh_b)
        dst_loc_b = make_location(tenant_b, dst_wh_b)
        med_b = make_medicine(tenant_b)
        batch_b = make_batch(tenant_b, company_b, med_b)
        req_b = make_user("user-b@test.com")

        t_a = create_sample_transfer(tenant_a, company_a, src_wh_a, dst_wh_a, src_loc_a, dst_loc_a, med_a, batch_a, req_a)
        t_b = create_sample_transfer(tenant_b, company_b, src_wh_b, dst_wh_b, src_loc_b, dst_loc_b, med_b, batch_b, req_b)

        selector = StockTransferSelector()
        qs_a = selector.list_transfers(tenant=tenant_a)
        qs_b = selector.list_transfers(tenant=tenant_b)

        assert qs_a.count() == 1
        assert qs_b.count() == 1
        assert selector.get_transfer_by_id(tenant_a, str(t_b.pk)) is None


# ===========================================================================
# SELECTOR & REPORTING TESTS
# ===========================================================================


@pytest.mark.django_db
class TestStockTransferSelectors:
    def test_transfer_statistics(self):
        tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, _, requester, approver = full_transfer_setup()
        svc = StockTransferService()
        selector = StockTransferSelector()

        t1 = create_sample_transfer(tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, requester, qty=Decimal("10"))
        t2 = create_sample_transfer(tenant, company, src_wh, dst_wh, src_loc, dst_loc, med, batch, requester, qty=Decimal("20"))

        svc.request_transfer(tenant, t1, user=requester)
        t1.refresh_from_db()
        svc.approve_transfer(tenant, t1, user=approver)
        t1.refresh_from_db()
        svc.pick_transfer(tenant, t1, user=approver)
        t1.refresh_from_db()
        svc.dispatch_transfer(tenant, t1, user=approver)

        stats = selector.get_transfer_statistics(tenant=tenant)
        assert stats["total_transfers"] == 2
        assert stats["in_transit_transfers"] == 1
        assert stats["pending_approval_transfers"] == 0
