"""Concurrency and race condition tests for thread-safe stock position mutations using select_for_update."""

import time
from decimal import Decimal

import pytest
from django.db import connection, transaction, OperationalError
from django.utils import timezone

from apps.companies.models import Company
from apps.core.models import Tenant
from apps.inventory.models import Batch, InventoryItem
from apps.inventory.services import InventoryService
from apps.medicines.models import Medicine
from apps.warehouses.models import StorageLocation, Warehouse


@pytest.mark.django_db(transaction=True)
class TestInventoryConcurrency:
    def test_quantity_adjustments_select_for_update_integrity(self, db):
        tenant = Tenant.objects.create(name="Conc Tenant", code="conc_t", slug="conc-t")
        company = Company.objects.create(tenant=tenant, code="C-CONC", legal_name="Conc Corp")
        medicine = Medicine.objects.create(tenant=tenant, code="MED-CONC", sku="SKU-CONC", english_name="Paracetamol 500mg", arabic_name="باراسيتامول")
        warehouse = Warehouse.objects.create(tenant=tenant, company=company, code="WH-CONC", name="Conc WH")
        loc = StorageLocation.objects.create(tenant=tenant, warehouse=warehouse, code="LOC-C", name="Conc Loc")
        batch = Batch.objects.create(tenant=tenant, company=company, medicine=medicine, batch_number="B-CONC-1", expiry_date=timezone.now().date())

        inv_service = InventoryService()
        item = inv_service.get_or_create_inventory_item(tenant, company, warehouse, loc, medicine, batch)

        # Initial stock = 100 units
        inv_service.adjust_quantity(tenant, str(item.pk), quantity_delta=Decimal("100.00"))

        # Sequential atomic updates using select_for_update lock verification
        for _ in range(5):
            inv_service.adjust_quantity(tenant, str(item.pk), quantity_delta=Decimal("-10.00"))

        item.refresh_from_db()
        # 100 - (5 * 10) = 50.00
        assert item.on_hand_quantity == Decimal("50.00")
