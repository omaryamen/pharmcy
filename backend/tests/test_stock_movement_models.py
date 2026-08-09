"""Unit tests for Stock Movement domain models."""

from decimal import Decimal

import pytest
from django.utils import timezone

from apps.companies.models import Company
from apps.core.models import Tenant
from apps.inventory.models import Batch
from apps.medicines.models import Medicine
from apps.stock_movement.models import MovementStatus, MovementType, StockMovement, StockMovementLine
from apps.stock_movement.services import MovementNumberGenerator
from apps.warehouses.models import StorageLocation, Warehouse


@pytest.mark.django_db
class TestStockMovementModels:
    def test_stock_movement_creation_and_number_generation(self, db):
        tenant = Tenant.objects.create(name="Stk Mod Tenant", code="stk_mod_t", slug="stk-mod-t")
        company = Company.objects.create(tenant=tenant, code="C-SM", legal_name="SM Corp")
        warehouse = Warehouse.objects.create(tenant=tenant, company=company, code="WH-SM", name="SM WH")

        generator = MovementNumberGenerator()
        num1 = generator.generate_number(tenant, MovementType.RECEIPT)
        assert num1.startswith("REC-")

        movement = StockMovement.objects.create(
            tenant=tenant,
            company=company,
            warehouse=warehouse,
            movement_number=num1,
            movement_type=MovementType.RECEIPT,
            quantity=Decimal("100.00"),
            unit_cost=Decimal("10.0000"),
            total_cost=Decimal("1000.0000"),
        )

        assert movement.movement_number == num1
        assert movement.movement_status == MovementStatus.DRAFT
        assert movement.quantity == Decimal("100.00")

    def test_stock_movement_line_total_cost_calculation(self, db):
        tenant = Tenant.objects.create(name="Line Cost Tenant", code="lc_t", slug="lc-t")
        company = Company.objects.create(tenant=tenant, code="C-LC", legal_name="LC Corp")
        warehouse = Warehouse.objects.create(tenant=tenant, company=company, code="WH-LC", name="LC WH")
        medicine = Medicine.objects.create(tenant=tenant, code="MED-LC", sku="SKU-LC", english_name="Amoxicillin 250mg", arabic_name="أموكسيسيلين")

        movement = StockMovement.objects.create(
            tenant=tenant,
            company=company,
            warehouse=warehouse,
            movement_number="REC-2026-000002",
            movement_type=MovementType.RECEIPT,
        )

        line = StockMovementLine.objects.create(
            tenant=tenant,
            movement=movement,
            medicine=medicine,
            quantity=Decimal("50.00"),
            unit_cost=Decimal("4.5000"),
        )

        assert line.total_cost == Decimal("225.0000")
