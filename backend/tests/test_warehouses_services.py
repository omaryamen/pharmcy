"""Unit & Integration tests for Enterprise Warehouse Management services."""

import pytest
from apps.companies.models import Company
from apps.core.models import Tenant
from apps.warehouses.exceptions import (
    DuplicateWarehouseCodeError,
    DuplicateWarehouseNameError,
    WarehouseDeleteForbiddenError,
)
from apps.warehouses.services import StorageLocationService, WarehouseService


@pytest.mark.django_db
class TestWarehouseServices:
    def test_create_and_update_warehouse(self, db):
        tenant = Tenant.objects.create(name="WH Serv Tenant", code="wh_serv_t", slug="wh-serv-t")
        company = Company.objects.create(tenant=tenant, code="C-SERV", legal_name="Serv Corp")
        service = WarehouseService()

        warehouse = service.create_warehouse(
            tenant=tenant,
            company=company,
            code="WH-SERV-01",
            name="Service Central WH",
            city="Sanaa",
            warehouse_type="main",
        )

        assert warehouse.code == "wh-serv-01"
        assert warehouse.name == "Service Central WH"

        updated = service.update_warehouse(warehouse, phone="+967771112233", city="Aden")
        assert updated.phone == "+967771112233"
        assert updated.city == "Aden"

    def test_duplicate_code_and_name_prevention(self, db):
        tenant = Tenant.objects.create(name="WH Dup Tenant", code="wh_dup_t", slug="wh-dup-t")
        company = Company.objects.create(tenant=tenant, code="C-DUP", legal_name="Dup Corp")
        service = WarehouseService()

        service.create_warehouse(tenant=tenant, company=company, code="WH-UNIQUE", name="Unique Name")

        with pytest.raises(DuplicateWarehouseCodeError):
            service.create_warehouse(tenant=tenant, company=company, code="WH-UNIQUE", name="Other Name")

        with pytest.raises(DuplicateWarehouseNameError):
            service.create_warehouse(tenant=tenant, company=company, code="WH-OTHER", name="Unique Name")

    def test_delete_forbidden_when_locations_exist(self, db):
        tenant = Tenant.objects.create(name="WH Del Tenant", code="wh_del_t", slug="wh-del-t")
        company = Company.objects.create(tenant=tenant, code="C-DEL", legal_name="Del Corp")
        wh_service = WarehouseService()
        loc_service = StorageLocationService()

        warehouse = wh_service.create_warehouse(tenant=tenant, company=company, code="WH-DEL-01", name="Del WH")
        loc_service.create_location(tenant, warehouse, code="ZONE-1", name="Zone 1")

        with pytest.raises(WarehouseDeleteForbiddenError):
            wh_service.soft_delete_warehouse(warehouse)
