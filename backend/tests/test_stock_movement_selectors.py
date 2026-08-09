"""Unit tests for StockMovement selectors and traceability reporting."""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.companies.models import Company
from apps.core.models import Tenant
from apps.inventory.models import Batch
from apps.medicines.models import Medicine
from apps.stock_movement.selectors import StockMovementSelector
from apps.stock_movement.services import StockMovementEngine
from apps.warehouses.models import StorageLocation, Warehouse


@pytest.mark.django_db
class TestStockMovementSelectors:
    def test_medicine_and_batch_traceability_lookup(self, db):
        tenant = Tenant.objects.create(name="Sel Tenant", code="sel_t", slug="sel-t")
        company = Company.objects.create(tenant=tenant, code="C-SEL", legal_name="Sel Corp")
        wh = Warehouse.objects.create(tenant=tenant, company=company, code="WH-SEL", name="Sel WH")
        loc = StorageLocation.objects.create(tenant=tenant, warehouse=wh, code="LOC-SEL", name="Sel Loc")
        medicine = Medicine.objects.create(tenant=tenant, code="MED-SEL", sku="SKU-SEL", english_name="Metformin 500mg", arabic_name="ميتفورمين")
        batch = Batch.objects.create(tenant=tenant, company=company, medicine=medicine, batch_number="B-SEL-99", expiry_date=timezone.now().date() + timedelta(days=250))

        engine = StockMovementEngine()
        engine.receive_stock(tenant=tenant, company=company, warehouse=wh, location=loc, medicine=medicine, batch=batch, quantity=Decimal("100.00"))
        engine.issue_stock(tenant=tenant, company=company, warehouse=wh, location=loc, medicine=medicine, batch=batch, quantity=Decimal("20.00"))

        selector = StockMovementSelector()

        # Medicine traceability
        med_trace = list(selector.get_medicine_traceability(tenant, str(medicine.pk)))
        assert len(med_trace) == 2

        # Batch traceability
        batch_trace = list(selector.get_batch_traceability(tenant, str(batch.pk)))
        assert len(batch_trace) == 2

        # Movement statistics
        stats = selector.get_movement_statistics(tenant, company_id=str(company.pk))
        assert stats["total_movements"] == 2
        assert stats["completed_movements"] == 2
