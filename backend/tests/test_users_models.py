"""Unit tests for Enterprise User Management models."""

import pytest
from django.contrib.auth import get_user_model

from apps.branches.models import Branch
from apps.companies.models import Company
from apps.core.models import Tenant
from apps.users.models import EmployeeProfile, EmploymentType, Gender

User = get_user_model()


@pytest.mark.django_db
class TestUserModels:
    def test_create_user_and_employee_profile(self, db):
        tenant = Tenant.objects.create(name="Tenant Users", code="t_users", slug="tenant-users")
        company = Company.objects.create(tenant=tenant, legal_name="Sanaa Pharma", code="sanaa_p", slug="sanaa-p")
        branch = Branch.objects.create(tenant=tenant, company=company, name="Branch 1", code="b1", slug="b-1")

        user = User.objects.create_user(
            email="employee1@sanaapharma.com",
            first_name="Tariq",
            last_name="Al-Ahdal",
            password="Password123!",
        )
        user.tenants.add(tenant)

        profile = EmployeeProfile.objects.create(
            user=user,
            tenant=tenant,
            company=company,
            primary_branch=branch,
            employee_number="EMP-1001",
            arabic_name="طارق الأهدل",
            gender=Gender.MALE,
            employment_type=EmploymentType.FULL_TIME,
            job_title="Senior Pharmacist",
            department="Dispensing",
        )
        profile.branches.add(branch)

        assert profile.pk is not None
        assert profile.user == user
        assert profile.company == company
        assert profile.primary_branch == branch
        assert str(profile) == "Profile for employee1@sanaapharma.com (Tariq Al-Ahdal)"
