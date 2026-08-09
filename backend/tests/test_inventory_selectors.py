"""Unit tests for Inventory and Batch selectors (FEFO, Recall Readiness, Expiry alerts)."""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.companies.models import Company
from apps.core.models import Tenant
from apps.inventory.models import Batch
from apps.inventory.selectors import BatchSelector, InventoryItemSelector
from apps.inventory.services import InventoryService
from apps.medicines.models import Medicine
from apps.warehouses.models import StorageLocation, Warehouse


@pytest.mark.django_db
class TestInventorySelectors:
    def test_fefo_selection_orders_by_earliest_expiry(self, db):
        tenant = Tenant.objects.create(name="FEFO Tenant", code="fefo_t", slug="fefo-t")
        company = Company.objects.create(tenant=tenant, code="C-FEFO", legal_name="FEFO Corp")
        medicine = Medicine.objects.create(tenant=tenant, code="MED-FEFO", sku="SKU-FEFO", english_name="Augmentin 1g", arabic_name="أوجمنتين")

        today = timezone.now().date()
        exp_later = today + timedelta(days=365)
        exp_sooner = today + timedelta(days=60)
        exp_mid = today + timedelta(days=120)

        batch_late = Batch.objects.create(tenant=tenant, company=company, medicine=medicine, batch_number="B-LATE", expiry_date=exp_later)
        batch_soon = Batch.objects.create(tenant=tenant, company=company, medicine=medicine, batch_number="B-SOON", expiry_date=exp_sooner)
        batch_mid = Batch.objects.create(tenant=tenant, company=company, medicine=medicine, batch_number="B-MID", expiry_date=exp_mid)

        batch_selector = BatchSelector()
        fefo_batches = list(batch_selector.get_available_batches_fefo(tenant, medicine_id=str(medicine.pk)))

        assert len(fefo_batches) == 3
        # Should be ordered B-SOON -> B-MID -> B-LATE
        assert fefo_batches[0].batch_number == "B-SOON"
        assert fefo_batches[1].batch_number == "B-MID"
        assert fefo_batches[2].batch_number == "B-LATE"

    def test_recall_readiness_lookup(self, db):
        tenant = Tenant.objects.create(name="Recall Tenant", code="rec_t", slug="rec-t")
        company = Company.objects.create(tenant=tenant, code="C-REC", legal_name="Recall Corp")
        medicine = Medicine.objects.create(tenant=tenant, code="MED-REC", sku="SKU-REC", english_name="Zantac 150mg", arabic_name="زنتاك")
        wh1 = Warehouse.objects.create(tenant=tenant, company=company, code="WH-1", name="Main Warehouse")
        loc1 = StorageLocation.objects.create(tenant=tenant, warehouse=wh1, code="LOC-1", name="Loc 1")
        wh2 = Warehouse.objects.create(tenant=tenant, company=company, code="WH-2", name="Branch Warehouse")
        loc2 = StorageLocation.objects.create(tenant=tenant, warehouse=wh2, code="LOC-2", name="Loc 2")

        batch = Batch.objects.create(tenant=tenant, company=company, medicine=medicine, batch_number="RECALL-99", expiry_date=timezone.now().date() + timedelta(days=200))
        inv_service = InventoryService()

        item1 = inv_service.get_or_create_inventory_item(tenant, company, wh1, loc1, medicine, batch)
        inv_service.adjust_quantity(tenant, str(item1.pk), quantity_delta=Decimal("50.00"))

        item2 = inv_service.get_or_create_inventory_item(tenant, company, wh2, loc2, medicine, batch)
        inv_service.adjust_quantity(tenant, str(item2.pk), quantity_delta=Decimal("30.00"))

        item_selector = InventoryItemSelector()
        recalled_positions = list(item_selector.find_inventory_for_recall(tenant, batch_number="RECALL-99"))

        assert len(recalled_positions) == 2
        warehouses = {pos.warehouse.code for pos in recalled_positions}
        assert "WH-1" in warehouses
        assert "WH-2" in warehouses
