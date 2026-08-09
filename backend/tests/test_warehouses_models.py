"""Unit tests for Warehouse & StorageLocation domain models."""

import pytest
from apps.companies.models import Company
from apps.core.models import Tenant
from apps.warehouses.models import LocationStatus, StorageLocation, Warehouse, WarehouseStatus, WarehouseType


@pytest.mark.django_db
class TestWarehouseModels:
    def test_warehouse_model_creation_and_defaults(self, db):
        tenant = Tenant.objects.create(name="WH Model Tenant", code="wh_mod_t", slug="wh-mod-t")
        company = Company.objects.create(tenant=tenant, code="C-WH", legal_name="WH Company Ltd")

        warehouse = Warehouse.objects.create(
            tenant=tenant,
            company=company,
            code="wh-main-01",
            name="Sanaa Central Warehouse",
            arabic_name="مستودع صنعاء المركزي",
            warehouse_type=WarehouseType.MAIN,
            city="Sanaa",
        )

        assert warehouse.code == "wh-main-01"
        assert warehouse.name == "Sanaa Central Warehouse"
        assert warehouse.display_name == "مستودع صنعاء المركزي"
        assert warehouse.status == WarehouseStatus.ACTIVE
        assert warehouse.is_deleted is False

    def test_warehouse_status_lifecycle(self, db):
        tenant = Tenant.objects.create(name="WH Status Tenant", code="wh_st_t", slug="wh-st-t")
        company = Company.objects.create(tenant=tenant, code="C-ST", legal_name="Status Corp")
        warehouse = Warehouse.objects.create(
            tenant=tenant,
            company=company,
            code="wh-st-01",
            name="Status Warehouse",
        )

        warehouse.deactivate()
        assert warehouse.status == WarehouseStatus.INACTIVE

        warehouse.suspend()
        assert warehouse.status == WarehouseStatus.SUSPENDED

        warehouse.close_temporarily()
        assert warehouse.status == WarehouseStatus.TEMPORARILY_CLOSED

        warehouse.activate()
        assert warehouse.status == WarehouseStatus.ACTIVE

        warehouse.delete()
        assert warehouse.is_deleted is True
        assert warehouse.deleted_at is not None

        warehouse.restore()
        assert warehouse.is_deleted is False
        assert warehouse.status == WarehouseStatus.ACTIVE
