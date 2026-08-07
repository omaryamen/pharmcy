"""Unit & Integration tests for Enterprise Supplier Management services."""

import pytest

from apps.core.models import Tenant
from apps.suppliers.exceptions import DuplicateSupplierCodeError, DuplicateSupplierLegalNameError
from apps.suppliers.services import SupplierService


@pytest.mark.django_db
class TestSupplierServices:
    def test_create_and_update_supplier_service(self, db):
        tenant = Tenant.objects.create(name="Tenant Sup Serv", code="t_sup_srv", slug="tenant-sup-srv")
        service = SupplierService()

        supplier = service.create_supplier(
            tenant=tenant,
            code="SUP-100",
            legal_name="Al-Hikma Wholesale Corp",
            display_name="Al-Hikma",
            email="info@alhikma.com",
            phone="+9671234567",
        )

        assert supplier.code == "sup-100"
        assert supplier.legal_name == "Al-Hikma Wholesale Corp"

        updated = service.update_supplier(supplier, phone="+9677777777")
        assert updated.phone == "+9677777777"

    def test_duplicate_code_and_legal_name_prevention(self, db):
        tenant = Tenant.objects.create(name="Tenant Sup Dup", code="t_sup_d", slug="tenant-sup-d")
        service = SupplierService()

        service.create_supplier(tenant=tenant, code="SUP-DUP", legal_name="Unique Supplier Name")

        with pytest.raises(DuplicateSupplierCodeError):
            service.create_supplier(tenant=tenant, code="SUP-DUP", legal_name="Another Supplier Name")

        with pytest.raises(DuplicateSupplierLegalNameError):
            service.create_supplier(tenant=tenant, code="SUP-OTHER", legal_name="Unique Supplier Name")

    def test_bulk_import_suppliers(self, db):
        tenant = Tenant.objects.create(name="Tenant Sup Bulk", code="t_sup_b", slug="tenant-sup-b")
        service = SupplierService()

        items = [
            {"code": "SUP-B1", "legal_name": "Supplier One", "display_name": "Sup One"},
            {"code": "SUP-B2", "legal_name": "Supplier Two", "display_name": "Sup Two"},
        ]

        result = service.bulk_import_suppliers(tenant=tenant, company=None, items=items)
        assert result["created"] == 2
        assert len(result["errors"]) == 0
