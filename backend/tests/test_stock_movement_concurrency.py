"""Concurrency and atomicity tests for StockMovementEngine."""

from decimal import Decimal

import pytest
from django.utils import timezone

from apps.companies.models import Company
from apps.core.models import Tenant
from apps.inventory.exceptions import InsufficientStockError
from apps.inventory.models import Batch, InventoryItem
from apps.medicines.models import Medicine
from apps.stock_movement.services import StockMovementEngine
from apps.warehouses.models import StorageLocation, Warehouse


@pytest.mark.django_db
class TestStockMovementConcurrency:
    def test_insufficient_stock_rejects_outgoing_issue_atomically(self, db):
        tenant = Tenant.objects.create(name="Conc SM Tenant", code="c_sm_t", slug="c-sm-t")
        company = Company.objects.create(tenant=tenant, code="C-CSM", legal_name="CSM Corp")
        wh = Warehouse.objects.create(tenant=tenant, company=company, code="WH-CSM", name="CSM WH")
        loc = StorageLocation.objects.create(tenant=tenant, warehouse=wh, code="LOC-CSM", name="CSM Loc")
        medicine = Medicine.objects.create(tenant=tenant, code="MED-CSM", sku="SKU-CSM", english_name="Omeprazole 20mg", arabic_name="أوميبرازول")
        batch = Batch.objects.create(tenant=tenant, company=company, medicine=medicine, batch_number="B-CSM-1", expiry_date=timezone.now().date())

        engine = StockMovementEngine()
        engine.receive_stock(tenant=tenant, company=company, warehouse=wh, location=loc, medicine=medicine, batch=batch, quantity=Decimal("10.00"))

        # Issue 10 units succeeds
        engine.issue_stock(tenant=tenant, company=company, warehouse=wh, location=loc, medicine=medicine, batch=batch, quantity=Decimal("10.00"))

        from apps.inventory.exceptions import InsufficientStockError, NegativeStockForbiddenError
        with pytest.raises((InsufficientStockError, NegativeStockForbiddenError)):
            engine.issue_stock(tenant=tenant, company=company, warehouse=wh, location=loc, medicine=medicine, batch=batch, quantity=Decimal("1.00"))

        item = InventoryItem.objects.get(tenant=tenant, warehouse=wh, storage_location=loc, medicine=medicine, batch=batch)
        assert item.on_hand_quantity == Decimal("0.00")
