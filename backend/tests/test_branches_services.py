"""Unit & Integration tests for Branch Management services."""

import pytest
from django.contrib.auth import get_user_model

from apps.branches.exceptions import CompanyMismatchError, DuplicateBranchCodeError
from apps.branches.models import BranchStatus, BranchType
from apps.branches.services import BranchService, BranchSettingsService
from apps.companies.models import Company
from apps.core.models import Tenant

User = get_user_model()


@pytest.mark.django_db
class TestBranchServices:
    def test_branch_creation_and_auto_settings(self, db):
        tenant = Tenant.objects.create(name="Tenant Serv", code="t_serv", slug="tenant-serv")
        company = Company.objects.create(tenant=tenant, legal_name="Pharma Corp", code="pharma_corp", slug="pharma-corp")
        service = BranchService()

        branch = service.create_branch(
            tenant=tenant,
            company=company,
            name="Aden Central Pharmacy",
            code="aden_01",
            slug="aden-central-pharmacy",
            branch_type=BranchType.RETAIL_PHARMACY,
            city="Aden",
        )

        assert branch.name == "Aden Central Pharmacy"
        assert branch.status == BranchStatus.ACTIVE
        assert hasattr(branch, "settings")
        assert branch.settings.company == company

    def test_duplicate_code_or_name_in_same_company_prevention(self, db):
        tenant = Tenant.objects.create(name="Tenant Dup", code="t_dup", slug="tenant-dup")
        company = Company.objects.create(tenant=tenant, legal_name="Delta Co", code="delta_co", slug="delta-co")
        service = BranchService()

        service.create_branch(tenant=tenant, company=company, name="Taiz Branch", code="taiz_01", slug="taiz-01")

        with pytest.raises(DuplicateBranchCodeError):
            service.create_branch(tenant=tenant, company=company, name="Taiz Branch", code="taiz_other", slug="taiz-other")

        with pytest.raises(DuplicateBranchCodeError):
            service.create_branch(tenant=tenant, company=company, name="Other Name", code="taiz_01", slug="taiz-02")

    def test_company_mismatch_prevention(self, db):
        tenant_1 = Tenant.objects.create(name="Tenant 1", code="t1", slug="t-1")
        tenant_2 = Tenant.objects.create(name="Tenant 2", code="t2", slug="t-2")
        company_2 = Company.objects.create(tenant=tenant_2, legal_name="Co 2", code="co_2", slug="co-2")
        service = BranchService()

        with pytest.raises(CompanyMismatchError):
            service.create_branch(tenant=tenant_1, company=company_2, name="Invalid Branch", code="inv_01", slug="inv-01")

    def test_assign_manager_and_company_transfer(self, db):
        tenant = Tenant.objects.create(name="Tenant Mgr", code="t_mgr", slug="tenant-mgr")
        company_a = Company.objects.create(tenant=tenant, legal_name="Company A", code="co_a", slug="co-a")
        company_b = Company.objects.create(tenant=tenant, legal_name="Company B", code="co_b", slug="co-b")

        user = User.objects.create_user(email="manager@pharmacy.com", first_name="Manager")
        service = BranchService()

        branch = service.create_branch(tenant=tenant, company=company_a, name="Move Branch", code="move_01", slug="move-01")

        service.assign_manager(branch, user)
        assert branch.manager == user

        service.change_company(branch, company_b)
        assert branch.company == company_b
        assert branch.settings.company == company_b

    def test_branch_settings_update(self, db):
        tenant = Tenant.objects.create(name="Tenant Set", code="t_set", slug="tenant-set")
        company = Company.objects.create(tenant=tenant, legal_name="Co Set", code="co_set", slug="co-set")
        branch_service = BranchService()
        settings_service = BranchSettingsService()

        branch = branch_service.create_branch(tenant=tenant, company=company, name="Config Branch", code="cfg_01", slug="cfg-01")

        updated_settings = settings_service.update_settings(
            branch,
            invoice_prefix="CFG-INV",
            currency_override="USD",
        )
        assert updated_settings.invoice_prefix == "CFG-INV"
        assert updated_settings.currency_override == "USD"
