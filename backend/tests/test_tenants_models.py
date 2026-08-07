"""Unit tests for Tenant Management models."""

import pytest
from django.utils import timezone

from apps.core.models import Tenant, TenantStatus
from apps.tenants.models import (
    BillingCycle,
    BusinessType,
    DomainType,
    SSLStatus,
    SubscriptionPlan,
    SubscriptionStatus,
    TenantDomain,
    TenantProfile,
    TenantSettings,
    TenantSubscription,
)


@pytest.mark.django_db
class TestTenantModels:
    def test_create_tenant_with_profile_and_settings(self, db):
        tenant = Tenant.objects.create(
            name="Al-Amal Pharmacy",
            code="al_amal_01",
            slug="al-amal-pharmacy",
            status=TenantStatus.ACTIVE,
        )
        assert tenant.pk is not None
        assert str(tenant) == "Al-Amal Pharmacy"

        profile = TenantProfile.objects.create(
            tenant=tenant,
            legal_name="Al-Amal Pharmacy Ltd",
            business_type=BusinessType.INDEPENDENT_PHARMACY,
            tax_number="TAX-998877",
            country="Yemen",
            city="Sana'a",
            currency="YER",
        )
        assert profile.tenant == tenant
        assert str(profile) == "Profile for Al-Amal Pharmacy Ltd"

        settings_obj = TenantSettings.objects.create(tenant=tenant)
        assert settings_obj.tenant == tenant
        assert settings_obj.tax_configuration["default_tax_rate"] == 15.0
        assert settings_obj.feature_flags["enable_pos"] is True

    def test_tenant_subscription_and_domain(self, db):
        tenant = Tenant.objects.create(name="Hope Chain", code="hope_chain", slug="hope-chain")

        sub = TenantSubscription.objects.create(
            tenant=tenant,
            plan=SubscriptionPlan.PROFESSIONAL,
            billing_cycle=BillingCycle.ANNUAL,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=365),
            max_users=50,
            max_branches=10,
        )
        assert sub.is_active_subscription is True
        assert sub.max_users == 50

        domain = TenantDomain.objects.create(
            tenant=tenant,
            domain_name="hope-chain.pharmacloud.local",
            domain_type=DomainType.SUBDOMAIN,
            is_verified=True,
            ssl_status=SSLStatus.ACTIVE,
            is_primary=True,
        )
        assert domain.is_primary is True
        assert domain.verification_token != ""

    def test_tenant_lifecycle_transitions(self, db):
        tenant = Tenant.objects.create(name="Test Tenant", code="test_t", slug="test-t", status=TenantStatus.TRIAL)

        tenant.activate()
        assert tenant.status == TenantStatus.ACTIVE
        assert tenant.is_active is True

        tenant.suspend()
        assert tenant.status == TenantStatus.SUSPENDED
        assert tenant.is_active is False

        tenant.archive()
        assert tenant.status == TenantStatus.ARCHIVED
        assert tenant.is_active is False

        tenant.restore()
        assert tenant.status == TenantStatus.ACTIVE
        assert tenant.is_active is True
