"""Unit and integration tests for StockMovementEngine (Receipts, Issues, Transfers, Reversals, Idempotency, FEFO)."""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.companies.models import Company
from apps.core.models import Tenant
from apps.inventory.models import Batch, InventoryItem
from apps.inventory.selectors import InventoryItemSelector
from apps.medicines.models import Medicine
from apps.stock_movement.exceptions import (
    CannotReverseUnprocessedMovementError,
    MovementAlreadyReversedError,
)
from apps.stock_movement.models import MovementStatus, MovementType, StockMovement
from apps.stock_movement.services import StockMovementEngine
from apps.warehouses.models import StorageLocation, Warehouse


@pytest.mark.django_db
class TestStockMovementEngine:
    def test_stock_receipt_operation(self, db):
        tenant = Tenant.objects.create(name="Eng Rec Tenant", code="eng_rec_t", slug="eng-rec-t")
        company = Company.objects.create(tenant=tenant, code="C-ER", legal_name="ER Corp")
        wh = Warehouse.objects.create(tenant=tenant, company=company, code="WH-ER", name="ER WH")
        loc = StorageLocation.objects.create(tenant=tenant, warehouse=wh, code="LOC-ER", name="ER Loc")
        medicine = Medicine.objects.create(tenant=tenant, code="MED-ER", sku="SKU-ER", english_name="Paracetamol 500mg", arabic_name="باراسيتامول")
        batch = Batch.objects.create(tenant=tenant, company=company, medicine=medicine, batch_number="B-REC-1", expiry_date=timezone.now().date() + timedelta(days=300))

        engine = StockMovementEngine()
        movement = engine.receive_stock(
            tenant=tenant,
            company=company,
            warehouse=wh,
            location=loc,
            medicine=medicine,
            batch=batch,
            quantity=Decimal("100.00"),
            unit_cost=Decimal("12.0000"),
            reference_number="PO-1001",
            idempotency_key="IDEM-REC-1",
        )

        assert movement.movement_status == MovementStatus.COMPLETED
        assert movement.quantity == Decimal("100.00")

        # Verify physical inventory item was updated
        item = InventoryItem.objects.get(tenant=tenant, warehouse=wh, storage_location=loc, medicine=medicine, batch=batch)
        assert item.on_hand_quantity == Decimal("100.00")

    def test_idempotency_prevents_duplicate_stock_receipt(self, db):
        tenant = Tenant.objects.create(name="Idem Tenant", code="idem_t", slug="idem-t")
        company = Company.objects.create(tenant=tenant, code="C-IDEM", legal_name="Idem Corp")
        wh = Warehouse.objects.create(tenant=tenant, company=company, code="WH-IDEM", name="Idem WH")
        loc = StorageLocation.objects.create(tenant=tenant, warehouse=wh, code="LOC-IDEM", name="Idem Loc")
        medicine = Medicine.objects.create(tenant=tenant, code="MED-IDEM", sku="SKU-IDEM", english_name="Aspirin 100mg", arabic_name="أسبرين")
        batch = Batch.objects.create(tenant=tenant, company=company, medicine=medicine, batch_number="B-IDEM-1", expiry_date=timezone.now().date() + timedelta(days=300))

        engine = StockMovementEngine()
        key = "IDEM-DUP-KEY-100"

        mov1 = engine.receive_stock(tenant=tenant, company=company, warehouse=wh, location=loc, medicine=medicine, batch=batch, quantity=Decimal("50.00"), idempotency_key=key)
        mov2 = engine.receive_stock(tenant=tenant, company=company, warehouse=wh, location=loc, medicine=medicine, batch=batch, quantity=Decimal("50.00"), idempotency_key=key)

        assert mov1.id == mov2.id
        item = InventoryItem.objects.get(tenant=tenant, warehouse=wh, storage_location=loc, medicine=medicine, batch=batch)
        assert item.on_hand_quantity == Decimal("50.00")  # Only 50 received, not 100!

    def test_double_entry_stock_transfer(self, db):
        tenant = Tenant.objects.create(name="Trf Tenant", code="trf_t", slug="trf-t")
        company = Company.objects.create(tenant=tenant, code="C-TRF", legal_name="TRF Corp")
        src_wh = Warehouse.objects.create(tenant=tenant, company=company, code="WH-SRC", name="Source WH")
        dst_wh = Warehouse.objects.create(tenant=tenant, company=company, code="WH-DST", name="Dest WH")
        src_loc = StorageLocation.objects.create(tenant=tenant, warehouse=src_wh, code="LOC-SRC", name="Src Loc")
        dst_loc = StorageLocation.objects.create(tenant=tenant, warehouse=dst_wh, code="LOC-DST", name="Dst Loc")
        medicine = Medicine.objects.create(tenant=tenant, code="MED-TRF", sku="SKU-TRF", english_name="Ibuprofen 400mg", arabic_name="إيبوبروفين")
        batch = Batch.objects.create(tenant=tenant, company=company, medicine=medicine, batch_number="B-TRF-1", expiry_date=timezone.now().date() + timedelta(days=200))

        engine = StockMovementEngine()
        engine.receive_stock(tenant=tenant, company=company, warehouse=src_wh, location=src_loc, medicine=medicine, batch=batch, quantity=Decimal("100.00"))

        # Transfer 40 units from Source to Destination
        trf_mov = engine.transfer_stock(
            tenant=tenant,
            company=company,
            source_warehouse=src_wh,
            destination_warehouse=dst_wh,
            source_location=src_loc,
            destination_location=dst_loc,
            medicine=medicine,
            batch=batch,
            quantity=Decimal("40.00"),
        )

        assert trf_mov.movement_status == MovementStatus.COMPLETED

        src_item = InventoryItem.objects.get(tenant=tenant, warehouse=src_wh, storage_location=src_loc, medicine=medicine, batch=batch)
        dst_item = InventoryItem.objects.get(tenant=tenant, warehouse=dst_wh, storage_location=dst_loc, medicine=medicine, batch=batch)

        assert src_item.on_hand_quantity == Decimal("60.00")
        assert dst_item.on_hand_quantity == Decimal("40.00")

    def test_stock_reversal_creates_compensating_movement(self, db):
        tenant = Tenant.objects.create(name="Rev Tenant", code="rev_t", slug="rev-t")
        company = Company.objects.create(tenant=tenant, code="C-REV", legal_name="Rev Corp")
        wh = Warehouse.objects.create(tenant=tenant, company=company, code="WH-REV", name="Rev WH")
        loc = StorageLocation.objects.create(tenant=tenant, warehouse=wh, code="LOC-REV", name="Rev Loc")
        medicine = Medicine.objects.create(tenant=tenant, code="MED-REV", sku="SKU-REV", english_name="Ciprofloxacin 500mg", arabic_name="سيفروكسين")
        batch = Batch.objects.create(tenant=tenant, company=company, medicine=medicine, batch_number="B-REV-1", expiry_date=timezone.now().date() + timedelta(days=400))

        engine = StockMovementEngine()
        orig = engine.receive_stock(tenant=tenant, company=company, warehouse=wh, location=loc, medicine=medicine, batch=batch, quantity=Decimal("80.00"))

        item_before = InventoryItem.objects.get(tenant=tenant, warehouse=wh, storage_location=loc, medicine=medicine, batch=batch)
        assert item_before.on_hand_quantity == Decimal("80.00")

        # Reverse movement
        reversal = engine.reverse_movement(tenant, orig, reason="Data entry error")
        assert reversal.is_reversal is True
        assert reversal.reversed_movement == orig

        orig.refresh_from_db()
        assert orig.movement_status == MovementStatus.REVERSED

        item_after = InventoryItem.objects.get(tenant=tenant, warehouse=wh, storage_location=loc, medicine=medicine, batch=batch)
        assert item_after.on_hand_quantity == Decimal("0.00")

        # Attempting to reverse again raises MovementAlreadyReversedError
        with pytest.raises(MovementAlreadyReversedError):
            engine.reverse_movement(tenant, orig)
