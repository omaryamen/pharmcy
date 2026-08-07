"""Unit tests for Enterprise Supplier Management models."""

import pytest

from apps.core.models import Tenant
from apps.suppliers.models import RiskLevel, Supplier, SupplierStatus, SupplierType


@pytest.mark.django_db
class TestSupplierModels:
    def test_create_supplier_model(self, db):
        tenant = Tenant.objects.create(name="Tenant Sup Mod", code="t_sup_m", slug="tenant-sup-m")
        supplier = Supplier.objects.create(
            tenant=tenant,
            code="sup-001",
            legal_name="Yemen Pharma Supply Ltd",
            display_name="Yemen Pharma",
            supplier_type=SupplierType.DISTRIBUTOR,
            supplier_category="Pharmaceuticals",
            status=SupplierStatus.ACTIVE,
            risk_level=RiskLevel.LOW,
        )

        assert supplier.pk is not None
        assert str(supplier) == "Yemen Pharma (sup-001)"
        assert supplier.status == SupplierStatus.ACTIVE
        assert supplier.risk_level == RiskLevel.LOW

    def test_supplier_status_methods(self, db):
        tenant = Tenant.objects.create(name="Tenant Sup Stat", code="t_sup_s", slug="tenant-sup-s")
        supplier = Supplier.objects.create(
            tenant=tenant,
            code="sup-002",
            legal_name="Sanaa Medical Importers",
            display_name="Sanaa Medical",
        )

        supplier.suspend()
        assert supplier.status == SupplierStatus.SUSPENDED

        supplier.blacklist()
        assert supplier.status == SupplierStatus.BLACKLISTED
        assert supplier.is_blacklisted is True

        supplier.activate()
        assert supplier.status == SupplierStatus.ACTIVE
        assert supplier.is_blacklisted is False
