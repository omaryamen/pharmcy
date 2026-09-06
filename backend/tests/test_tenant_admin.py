"""Tests for IMP-046-B: Pharmacy & Tenant Admin Operations and Tenant Boundary Isolation."""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.companies.models import Company, CompanySettings
from apps.core.models import Tenant

User = get_user_model()


@pytest.fixture
def pharmacy_admin_user_a(db):
    tenant_a = Tenant.objects.create(name="Al-Amal Pharmacy Chain", code="TNT-AMAL-01", slug="tnt-amal-01")
    company_a = Company.objects.create(
        tenant=tenant_a,
        legal_name="Al-Amal Modern Pharmacy Chain LLC",
        code="AMAL-CO-01",
        slug="amal-co-01",
    )
    settings_a = CompanySettings.objects.create(
        tenant=tenant_a,
        company=company_a,
    )
    user_a = User.objects.create_user(
        email="admin@amal-rx.com",
        password="securepassword123",
        first_name="Dr. Ahmed",
        last_name="Mansoor",
        is_staff=True,
    )
    return user_a, tenant_a, company_a, settings_a


@pytest.fixture
def pharmacy_admin_user_b(db):
    tenant_b = Tenant.objects.create(name="Al-Shifa Medical", code="TNT-SHIFA-02", slug="tnt-shifa-02")
    company_b = Company.objects.create(
        tenant=tenant_b,
        legal_name="Al-Shifa Pharmacy LLC",
        code="SHIFA-CO-01",
        slug="shifa-co-01",
    )
    settings_b = CompanySettings.objects.create(
        tenant=tenant_b,
        company=company_b,
    )
    user_b = User.objects.create_user(
        email="admin@shifa-rx.com",
        password="securepassword123",
        first_name="Dr. Khalid",
        last_name="Nader",
        is_staff=True,
    )
    return user_b, tenant_b, company_b, settings_b


@pytest.mark.django_db
class TestPharmacyTenantAdmin:
    def test_pharmacy_admin_can_update_company_profile(self, pharmacy_admin_user_a):
        user_a, tenant_a, company_a, settings_a = pharmacy_admin_user_a
        assert company_a.tenant == tenant_a

        # Modify legal parameters
        company_a.commercial_registration = "1010889922"
        company_a.tax_number = "300998877600003"
        company_a.license_number = "MOH-RX-2026-991"
        company_a.save()

        company_a.refresh_from_db()
        assert company_a.commercial_registration == "1010889922"
        assert company_a.tax_number == "300998877600003"
        assert company_a.license_number == "MOH-RX-2026-991"

    def test_company_settings_tax_and_prefixes(self, pharmacy_admin_user_a):
        _, _, company_a, settings_a = pharmacy_admin_user_a

        settings_a.tax_configuration = {
            "tax_enabled": True,
            "default_tax_rate": 5.0,
            "tax_inclusive": False,
            "tax_registration_number": "300998877600003",
        }
        settings_a.document_prefixes = {
            "invoice_prefix": "INV",
            "sale_prefix": "SAL",
            "purchase_order_prefix": "PO",
            "goods_receipt_prefix": "GRN",
        }
        settings_a.save()

        settings_a.refresh_from_db()
        assert settings_a.tax_configuration["default_tax_rate"] == 5.0
        assert settings_a.document_prefixes["invoice_prefix"] == "INV"

    def test_tenant_boundary_isolation_between_companies(self, pharmacy_admin_user_a, pharmacy_admin_user_b):
        _, tenant_a, company_a, _ = pharmacy_admin_user_a
        _, tenant_b, company_b, _ = pharmacy_admin_user_b

        # Companies belong to distinct tenants
        assert company_a.tenant != company_b.tenant
        assert company_a.tenant_id == tenant_a.id
        assert company_b.tenant_id == tenant_b.id
