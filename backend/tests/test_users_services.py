"""Unit & Integration tests for Enterprise User Management services."""

import pytest
from django.contrib.auth import get_user_model

from apps.branches.models import Branch
from apps.companies.models import Company
from apps.core.models import Tenant
from apps.rbac.models import Role
from apps.users.exceptions import BranchCompanyMismatchError, DuplicateUserEmailError
from apps.users.services import UserService

User = get_user_model()


@pytest.mark.django_db
class TestUserServices:
    def test_create_enterprise_user_and_auto_profile(self, db):
        tenant = Tenant.objects.create(name="Tenant Serv USR", code="t_serv_u", slug="tenant-serv-u")
        company = Company.objects.create(tenant=tenant, legal_name="Apex Healthcare", code="apex_hc", slug="apex-hc")
        branch = Branch.objects.create(tenant=tenant, company=company, name="Apex HQ", code="apex_hq", slug="apex-hq")
        role = Role.objects.create(tenant=tenant, name="Pharmacist Role", code="pharmacist_role")

        service = UserService()

        user = service.create_enterprise_user(
            tenant=tenant,
            company=company,
            primary_branch=branch,
            email="pharmacist@apex.com",
            first_name="Salem",
            last_name="Ba-Obaid",
            employee_number="EMP-2001",
            job_title="Lead Pharmacist",
            roles=[role],
            branches=[branch],
        )

        assert user.email == "pharmacist@apex.com"
        assert user.is_active is True
        assert hasattr(user, "employee_profile")
        assert user.employee_profile.company == company
        assert user.employee_profile.primary_branch == branch
        assert user.role_assignments.filter(role=role).exists()

    def test_duplicate_email_prevention(self, db):
        tenant = Tenant.objects.create(name="Tenant Dup USR", code="t_dup_u", slug="tenant-dup-u")
        company = Company.objects.create(tenant=tenant, legal_name="Biotest Ltd", code="biotest", slug="biotest")
        branch = Branch.objects.create(tenant=tenant, company=company, name="Bio 1", code="bio1", slug="bio-1")
        service = UserService()

        service.create_enterprise_user(
            tenant=tenant, company=company, primary_branch=branch, email="dup@biotest.com", first_name="User"
        )

        with pytest.raises(DuplicateUserEmailError):
            service.create_enterprise_user(
                tenant=tenant, company=company, primary_branch=branch, email="dup@biotest.com", first_name="Other"
            )

    def test_company_branch_mismatch_prevention(self, db):
        tenant_1 = Tenant.objects.create(name="T1", code="t1_u", slug="t1-u")
        tenant_2 = Tenant.objects.create(name="T2", code="t2_u", slug="t2-u")
        company_2 = Company.objects.create(tenant=tenant_2, legal_name="Co2", code="co2", slug="co2")
        branch_2 = Branch.objects.create(tenant=tenant_2, company=company_2, name="Br2", code="br2", slug="br2")
        service = UserService()

        with pytest.raises(BranchCompanyMismatchError):
            service.create_enterprise_user(
                tenant=tenant_1, company=company_2, primary_branch=branch_2, email="invalid@mismatch.com", first_name="Bad"
            )

    def test_user_lifecycle_lock_unlock_password_reset(self, db):
        tenant = Tenant.objects.create(name="Tenant Life USR", code="t_life_u", slug="tenant-life-u")
        company = Company.objects.create(tenant=tenant, legal_name="Bio Pharma", code="bio_p", slug="bio-p")
        branch = Branch.objects.create(tenant=tenant, company=company, name="Br Main", code="b_main", slug="b-main")
        service = UserService()

        user = service.create_enterprise_user(
            tenant=tenant, company=company, primary_branch=branch, email="user@biopharma.com", first_name="Test"
        )

        service.lock_user(user)
        assert user.status == "locked"
        assert user.is_active is False

        service.unlock_user(user)
        assert user.status == "active"
        assert user.is_active is True

        service.reset_password(user, "NewSecret123!")
        assert user.check_password("NewSecret123!") is True
