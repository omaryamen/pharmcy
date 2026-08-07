"""Unit & Integration tests for Tenant Management services."""

import pytest
from django.contrib.auth import get_user_model

from apps.core.models import TenantStatus
from apps.rbac.models import Role
from apps.tenants.exceptions import DuplicateSlugError, TenantLimitExceededError, TenantStatusError
from apps.tenants.models import SubscriptionPlan
from apps.tenants.services import (
    TenantDomainService,
    TenantLifecycleService,
    TenantProvisioningService,
    TenantSettingsService,
    TenantSubscriptionService,
)

User = get_user_model()


@pytest.mark.django_db
class TestTenantServices:
    def test_tenant_provisioning_workflow(self, db):
        provisioner = TenantProvisioningService()
        tenant = provisioner.provision_tenant(
            name="Alpha Pharmacy",
            slug="alpha-pharmacy",
            code="alpha_ph",
            admin_email="admin@alphapharm.com",
            admin_password="SecurePassword123!",
            plan=SubscriptionPlan.STARTER,
            country="Yemen",
            currency="YER",
        )

        assert tenant.slug == "alpha-pharmacy"
        assert tenant.profile.legal_name == "Alpha Pharmacy"
        assert tenant.settings.tenant == tenant
        assert tenant.subscription.plan == SubscriptionPlan.STARTER
        assert tenant.domains.filter(is_primary=True).exists()

        # Check default roles bootstrapped
        assert Role.objects.filter(tenant=tenant, code="admin").exists()
        assert Role.objects.filter(tenant=tenant, code="member").exists()

        # Check owner assignment
        assert tenant.owner is not None
        assert tenant.owner.email == "admin@alphapharm.com"

    def test_duplicate_slug_raises_error(self, db):
        provisioner = TenantProvisioningService()
        provisioner.provision_tenant(name="Beta Pharmacy", slug="beta-ph")

        with pytest.raises(DuplicateSlugError):
            provisioner.provision_tenant(name="Beta Duplicate", slug="beta-ph")

    def test_lifecycle_transitions_and_clone(self, db):
        provisioner = TenantProvisioningService()
        lifecycle = TenantLifecycleService()

        tenant = provisioner.provision_tenant(name="Original Pharmacy", slug="orig-ph")

        lifecycle.suspend_tenant(tenant)
        assert tenant.status == TenantStatus.SUSPENDED

        lifecycle.activate_tenant(tenant)
        assert tenant.status == TenantStatus.ACTIVE

        lifecycle.deactivate_tenant(tenant)
        assert tenant.status == TenantStatus.INACTIVE

        cloned = lifecycle.clone_tenant(tenant, new_name="Cloned Pharmacy", new_slug="cloned-ph")
        assert cloned.slug == "cloned-ph"
        assert cloned.profile.country == tenant.profile.country

    def test_quota_limits_checking(self, db):
        provisioner = TenantProvisioningService()
        sub_service = TenantSubscriptionService()

        tenant = provisioner.provision_tenant(
            name="Quota Test", slug="quota-test", admin_email="owner@quota.com", plan=SubscriptionPlan.TRIAL
        )

        # Trial allows max 5 users. Owner is user #1.
        subscription = tenant.subscription
        assert subscription.max_users == 5

        # Creating 4 additional users (total 5)
        for i in range(4):
            u = User.objects.create_user(email=f"user{i}@quota.com", first_name="Test")
            u.tenants.add(tenant)

        assert tenant.users.count() == 5

        # Next addition should raise quota exception
        with pytest.raises(TenantLimitExceededError):
            sub_service.check_user_quota(tenant, requested_addition=1)

    def test_custom_domain_management(self, db):
        provisioner = TenantProvisioningService()
        domain_service = TenantDomainService()

        tenant = provisioner.provision_tenant(name="Domain Test", slug="domain-test")

        domain = domain_service.add_domain(tenant, domain_name="custom.pharmacy.com")
        assert domain.is_verified is False

        verified = domain_service.verify_domain(tenant, domain.pk)
        assert verified.is_verified is True

        primary = domain_service.set_primary_domain(tenant, domain.pk)
        assert primary.is_primary is True
