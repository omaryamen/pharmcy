"""Unit tests for Inventory & Batch domain models."""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.companies.models import Company
from apps.core.models import Tenant
from apps.inventory.exceptions import InvalidBatchDateError, NegativeStockForbiddenError
from apps.inventory.models import Batch, BatchStatus, InventoryItem, InventoryStatus
from apps.medicines.models import Medicine
from apps.warehouses.models import StorageLocation, Warehouse


@pytest.mark.django_db
class TestInventoryModels:
    def test_batch_creation_and_expiry_check(self, db):
        tenant = Tenant.objects.create(name="Inv Mod Tenant", code="inv_mod_t", slug="inv-mod-t")
        company = Company.objects.create(tenant=tenant, code="C-INV", legal_name="Inv Corp")
        medicine = Medicine.objects.create(tenant=tenant, code="MED-01", sku="SKU-01", english_name="Paracetamol 500mg", arabic_name="باراسيتامول")

        mfg_date = timezone.now().date() - timedelta(days=30)
        exp_date = timezone.now().date() + timedelta(days=365)

        batch = Batch.objects.create(
            tenant=tenant,
            company=company,
            medicine=medicine,
            batch_number="BATCH-2026-A",
            manufacturing_date=mfg_date,
            expiry_date=exp_date,
            unit_cost=Decimal("12.5000"),
            selling_price=Decimal("18.0000"),
        )

        assert batch.batch_number == "BATCH-2026-A"
        assert batch.is_expired is False
        assert batch.status == BatchStatus.ACTIVE

    def test_invalid_batch_dates_raises_error(self, db):
        tenant = Tenant.objects.create(name="Inv Date Tenant", code="inv_dt_t", slug="inv-dt-t")
        company = Company.objects.create(tenant=tenant, code="C-DT", legal_name="Date Corp")
        medicine = Medicine.objects.create(tenant=tenant, code="MED-02", sku="SKU-02", english_name="Amoxicillin 500mg", arabic_name="أموكسيسيلين")

        mfg_date = timezone.now().date()
        exp_date = timezone.now().date() - timedelta(days=10)

        with pytest.raises(InvalidBatchDateError):
            Batch.objects.create(
                tenant=tenant,
                company=company,
                medicine=medicine,
                batch_number="BATCH-INVALID",
                manufacturing_date=mfg_date,
                expiry_date=exp_date,
            )

    def test_inventory_item_quantities_and_available_calculation(self, db):
        tenant = Tenant.objects.create(name="Inv Qty Tenant", code="inv_qty_t", slug="inv-qty-t")
        company = Company.objects.create(tenant=tenant, code="C-QTY", legal_name="Qty Corp")
        medicine = Medicine.objects.create(tenant=tenant, code="MED-03", sku="SKU-03", english_name="Ibuprofen 400mg", arabic_name="إيبوبروفين")
        warehouse = Warehouse.objects.create(tenant=tenant, company=company, code="WH-QTY", name="Main WH")
        loc = StorageLocation.objects.create(tenant=tenant, warehouse=warehouse, code="ZONE-A", name="Zone A")

        exp_date = timezone.now().date() + timedelta(days=180)
        batch = Batch.objects.create(tenant=tenant, company=company, medicine=medicine, batch_number="B-IBU-101", expiry_date=exp_date)

        item = InventoryItem.objects.create(
            tenant=tenant,
            company=company,
            warehouse=warehouse,
            storage_location=loc,
            medicine=medicine,
            batch=batch,
            on_hand_quantity=Decimal("100.00"),
            reserved_quantity=Decimal("20.00"),
            damaged_quantity=Decimal("5.00"),
            quarantine_quantity=Decimal("10.00"),
            unit_cost=Decimal("5.0000"),
        )

        assert item.on_hand_quantity == Decimal("100.00")
        assert item.available_quantity == Decimal("65.00")  # 100 - 20 - 5 - 10
        assert item.total_cost_value == Decimal("500.0000")

    def test_negative_quantity_raises_error(self, db):
        tenant = Tenant.objects.create(name="Inv Neg Tenant", code="inv_neg_t", slug="inv-neg-t")
        company = Company.objects.create(tenant=tenant, code="C-NEG", legal_name="Neg Corp")
        medicine = Medicine.objects.create(tenant=tenant, code="MED-04", sku="SKU-04", english_name="Aspirin 100mg", arabic_name="أسبرين")
        warehouse = Warehouse.objects.create(tenant=tenant, company=company, code="WH-NEG", name="Neg WH")
        loc = StorageLocation.objects.create(tenant=tenant, warehouse=warehouse, code="BIN-1", name="Bin 1")
        batch = Batch.objects.create(tenant=tenant, company=company, medicine=medicine, batch_number="B-ASP-999", expiry_date=timezone.now().date() + timedelta(days=90))

        with pytest.raises(NegativeStockForbiddenError):
            InventoryItem.objects.create(
                tenant=tenant,
                company=company,
                warehouse=warehouse,
                storage_location=loc,
                medicine=medicine,
                batch=batch,
                on_hand_quantity=Decimal("-10.00"),
            )
