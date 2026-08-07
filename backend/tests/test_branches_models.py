"""Unit tests for Branch Management models."""

import pytest

from apps.branches.models import Branch, BranchSettings, BranchStatus, BranchType
from apps.companies.models import Company, CompanyStatus
from apps.core.models import Tenant, TenantStatus


@pytest.mark.django_db
class TestBranchModels:
    def test_create_branch_and_settings(self, db):
        tenant = Tenant.objects.create(name="Tenant Branch", code="t_branch", slug="tenant-branch", status=TenantStatus.ACTIVE)
        company = Company.objects.create(
            tenant=tenant,
            legal_name="Al-Shifa Co",
            code="shifa_co",
            slug="al-shifa-co",
            status=CompanyStatus.ACTIVE,
        )

        branch = Branch.objects.create(
            tenant=tenant,
            company=company,
            name="Main Branch Sanaa",
            code="sanaa_01",
            slug="main-branch-sanaa",
            branch_type=BranchType.RETAIL_PHARMACY,
            status=BranchStatus.ACTIVE,
            city="Sanaa",
        )

        assert branch.pk is not None
        assert str(branch) == "Main Branch Sanaa (Al-Shifa Co)"

        settings_obj = BranchSettings.objects.create(
            branch=branch,
            company=company,
            tenant=tenant,
            invoice_prefix="SAN-INV",
        )
        assert settings_obj.branch == branch
        assert settings_obj.invoice_prefix == "SAN-INV"
        assert settings_obj.tax_settings["tax_enabled"] is True

    def test_branch_status_lifecycle(self, db):
        tenant = Tenant.objects.create(name="Tenant Lifecycle", code="t_life", slug="tenant-life")
        company = Company.objects.create(tenant=tenant, legal_name="Gamma Co", code="gamma_co", slug="gamma-co")
        branch = Branch.objects.create(tenant=tenant, company=company, name="Branch Beta", code="branch_beta", slug="branch-beta")

        assert branch.status == BranchStatus.DRAFT

        branch.activate()
        assert branch.status == BranchStatus.ACTIVE

        branch.deactivate()
        assert branch.status == BranchStatus.INACTIVE

        branch.suspend()
        assert branch.status == BranchStatus.SUSPENDED

        branch.archive()
        assert branch.status == BranchStatus.ARCHIVED

        branch.restore()
        assert branch.status == BranchStatus.ACTIVE
