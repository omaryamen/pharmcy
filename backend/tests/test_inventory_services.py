"""Unit and Integration tests for Inventory and Batch domain services."""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.companies.models import Company
from apps.core.models import Tenant
from apps.inventory.exceptions import InsufficientStockError, NegativeStockForbiddenError
from apps.inventory.models import InventoryTransaction, TransactionType
from apps.inventory.services import BatchService, InventoryService
from apps.medicines.models import Medicine
from apps.warehouses.models import StorageLocation, Warehouse


@pytest.mark.django_db
class TestInventoryServices:
    def test_batch_service_lifecycle(self, db):
        tenant = Tenant.objects.create(name="Batch Serv Tenant", code="b_serv_t", slug="b-serv-t")
        company = Company.objects.create(tenant=tenant, code="C-BS", legal_name="Batch Corp")
        medicine = Medicine.objects.create(tenant=tenant, code="MED-BS", sku="SKU-BS", english_name="Ciprofloxacin 500mg", arabic_name="سيفروكسين")

        batch_service = BatchService()
        exp_date = timezone.now().date() + timedelta(days=200)

        batch = batch_service.create_batch(
            tenant=tenant,
            company=company,
            medicine=medicine,
            batch_number="B-CIP-001",
            expiry_date=exp_date,
            unit_cost=Decimal("15.0000"),
        )

        assert batch.batch_number == "B-CIP-001"
        assert batch.status == "active"

        blocked = batch_service.block_batch(batch)
        assert blocked.status == "blocked"

        unblocked = batch_service.unblock_batch(batch)
        assert unblocked.status == "active"

        recalled = batch_service.recall_batch(batch)
        assert recalled.status == "recalled"

    def test_inventory_service_adjustment_and_weighted_average_cost(self, db):
        tenant = Tenant.objects.create(name="Inv Adj Tenant", code="inv_adj_t", slug="inv-adj-t")
        company = Company.objects.create(tenant=tenant, code="C-IA", legal_name="Adj Corp")
        medicine = Medicine.objects.create(tenant=tenant, code="MED-IA", sku="SKU-IA", english_name="Omeprazole 20mg", arabic_name="أوميبرازول")
        warehouse = Warehouse.objects.create(tenant=tenant, company=company, code="WH-IA", name="Adj WH")
        loc = StorageLocation.objects.create(tenant=tenant, warehouse=warehouse, code="LOC-1", name="Loc 1")
        batch_service = BatchService()
        inv_service = InventoryService()

        batch = batch_service.create_batch(tenant=tenant, company=company, medicine=medicine, batch_number="B-OME-1", expiry_date=timezone.now().date() + timedelta(days=300))

        # Initial stock item creation
        item = inv_service.get_or_create_inventory_item(
            tenant=tenant,
            company=company,
            warehouse=warehouse,
            storage_location=loc,
            medicine=medicine,
            batch=batch,
            unit_cost=Decimal("10.0000"),
        )
        assert item.on_hand_quantity == Decimal("0.00")

        # 1st Stock Receipt (+100 @ 10.00)
        item, tx1 = inv_service.adjust_quantity(
            tenant=tenant,
            inventory_item_id=str(item.pk),
            quantity_delta=Decimal("100.00"),
            transaction_type=TransactionType.RECEIPT,
            unit_cost=Decimal("10.0000"),
        )
        assert item.on_hand_quantity == Decimal("100.00")
        assert item.average_cost == Decimal("10.0000")
        assert tx1.quantity == Decimal("100.00")

        # 2nd Stock Receipt (+100 @ 20.00) -> Average cost should update to 15.00
        item, tx2 = inv_service.adjust_quantity(
            tenant=tenant,
            inventory_item_id=str(item.pk),
            quantity_delta=Decimal("100.00"),
            transaction_type=TransactionType.RECEIPT,
            unit_cost=Decimal("20.0000"),
        )
        assert item.on_hand_quantity == Decimal("200.00")
        assert item.average_cost == Decimal("15.0000")
        assert tx2.quantity_before == Decimal("100.00")
        assert tx2.quantity_after == Decimal("200.00")

    def test_stock_reservation_and_release(self, db):
        tenant = Tenant.objects.create(name="Inv Res Tenant", code="inv_res_t", slug="inv-res-t")
        company = Company.objects.create(tenant=tenant, code="C-RES", legal_name="Res Corp")
        medicine = Medicine.objects.create(tenant=tenant, code="MED-RES", sku="SKU-RES", english_name="Metformin 500mg", arabic_name="ميتفورمين")
        warehouse = Warehouse.objects.create(tenant=tenant, company=company, code="WH-RES", name="Res WH")
        loc = StorageLocation.objects.create(tenant=tenant, warehouse=warehouse, code="LOC-RES", name="Res Loc")
        batch_service = BatchService()
        inv_service = InventoryService()

        batch = batch_service.create_batch(tenant=tenant, company=company, medicine=medicine, batch_number="B-MET-01", expiry_date=timezone.now().date() + timedelta(days=400))
        item = inv_service.get_or_create_inventory_item(tenant, company, warehouse, loc, medicine, batch)

        inv_service.adjust_quantity(tenant, str(item.pk), quantity_delta=Decimal("50.00"))

        # Reserve 20 units
        item, tx_res = inv_service.reserve_stock(tenant, str(item.pk), requested_quantity=Decimal("20.00"), reference_number="SO-1001")
        assert item.reserved_quantity == Decimal("20.00")
        assert item.available_quantity == Decimal("30.00")

        # Attempt to reserve more than available (35 units) -> InsufficientStockError
        with pytest.raises(InsufficientStockError):
            inv_service.reserve_stock(tenant, str(item.pk), requested_quantity=Decimal("35.00"))

        # Release reservation of 10 units
        item, tx_rel = inv_service.release_reservation(tenant, str(item.pk), release_quantity=Decimal("10.00"))
        assert item.reserved_quantity == Decimal("10.00")
        assert item.available_quantity == Decimal("40.00")
