"""Unit tests for Storage Location hierarchy, circular reference prevention, and tree pathing."""

import pytest
from apps.companies.models import Company
from apps.core.models import Tenant
from apps.warehouses.exceptions import CircularLocationHierarchyError, InvalidLocationWarehouseMismatchError
from apps.warehouses.models import StorageLocation, Warehouse
from apps.warehouses.services import StorageLocationService


@pytest.mark.django_db
class TestStorageLocationHierarchy:
    def test_location_full_path_breadcrumbs(self, db):
        tenant = Tenant.objects.create(name="Hierarchy Tenant", code="hier_t", slug="hier-t")
        company = Company.objects.create(tenant=tenant, code="C-H", legal_name="Hierarchy Corp")
        warehouse = Warehouse.objects.create(tenant=tenant, company=company, code="WH-H1", name="Main WH")

        service = StorageLocationService()
        zone = service.create_location(tenant, warehouse, code="ZONE-A", name="Zone A", location_type="zone")
        aisle = service.create_location(tenant, warehouse, code="AISLE-01", name="Aisle 1", parent=zone, location_type="aisle")
        rack = service.create_location(tenant, warehouse, code="RACK-03", name="Rack 3", parent=aisle, location_type="rack")
        shelf = service.create_location(tenant, warehouse, code="SHELF-02", name="Shelf 2", parent=rack, location_type="shelf")
        bin_loc = service.create_location(tenant, warehouse, code="BIN-07", name="Bin 7", parent=shelf, location_type="bin")

        assert bin_loc.get_full_path() == "ZONE-A / AISLE-01 / RACK-03 / SHELF-02 / BIN-07"
        assert str(bin_loc) == "WH-H1 / ZONE-A / AISLE-01 / RACK-03 / SHELF-02 / BIN-07"

    def test_circular_hierarchy_prevention(self, db):
        tenant = Tenant.objects.create(name="Circ Tenant", code="circ_t", slug="circ-t")
        company = Company.objects.create(tenant=tenant, code="C-C", legal_name="Circ Corp")
        warehouse = Warehouse.objects.create(tenant=tenant, company=company, code="WH-C1", name="Circ WH")

        service = StorageLocationService()
        loc_a = service.create_location(tenant, warehouse, code="LOC-A", name="Location A")
        loc_b = service.create_location(tenant, warehouse, code="LOC-B", name="Location B", parent=loc_a)
        loc_c = service.create_location(tenant, warehouse, code="LOC-C", name="Location C", parent=loc_b)

        # Attempt to set loc_a's parent to loc_c (creating A -> B -> C -> A loop)
        with pytest.raises(CircularLocationHierarchyError):
            service.move_location(loc_a, loc_c)

        # Attempt to set loc_a's parent to self
        with pytest.raises(CircularLocationHierarchyError):
            service.move_location(loc_a, loc_a)

    def test_cross_warehouse_parent_prevention(self, db):
        tenant = Tenant.objects.create(name="Cross Tenant", code="cross_t", slug="cross-t")
        company = Company.objects.create(tenant=tenant, code="C-CR", legal_name="Cross Corp")
        wh1 = Warehouse.objects.create(tenant=tenant, company=company, code="WH-1", name="WH One")
        wh2 = Warehouse.objects.create(tenant=tenant, company=company, code="WH-2", name="WH Two")

        service = StorageLocationService()
        loc_wh1 = service.create_location(tenant, wh1, code="LOC-WH1", name="Location in WH1")

        with pytest.raises(InvalidLocationWarehouseMismatchError):
            service.create_location(tenant, wh2, code="LOC-WH2", name="Location in WH2", parent=loc_wh1)
