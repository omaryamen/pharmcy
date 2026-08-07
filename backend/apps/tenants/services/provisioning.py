"""Tenant provisioning service: atomic creation of tenant, profile, settings, subscription, and admin."""

from __future__ import annotations

import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from apps.rbac.services import RoleAssignmentService, RoleBootstrapService
from apps.tenants.exceptions import DuplicateSlugError, InvalidSubscriptionError
from apps.tenants.models import (
    BillingCycle,
    DomainType,
    SubscriptionPlan,
    SubscriptionStatus,
    TenantDomain,
    TenantProfile,
    TenantSettings,
    TenantSubscription,
)
from apps.tenants.repositories import (
    TenantDomainRepository,
    TenantProfileRepository,
    TenantRepository,
    TenantSettingsRepository,
    TenantSubscriptionRepository,
)

logger = logging.getLogger(__name__)
User = get_user_model()


PLAN_QUOTAS = {
    SubscriptionPlan.TRIAL: {
        "max_users": 5,
        "max_branches": 1,
        "storage_limit_mb": 1024,
        "api_rate_limit_per_min": 1000,
    },
    SubscriptionPlan.STARTER: {
        "max_users": 10,
        "max_branches": 2,
        "storage_limit_mb": 5120,
        "api_rate_limit_per_min": 2000,
    },
    SubscriptionPlan.PROFESSIONAL: {
        "max_users": 50,
        "max_branches": 10,
        "storage_limit_mb": 20480,
        "api_rate_limit_per_min": 5000,
    },
    SubscriptionPlan.ENTERPRISE: {
        "max_users": 500,
        "max_branches": 100,
        "storage_limit_mb": 102400,
        "api_rate_limit_per_min": 10000,
    },
}


class TenantProvisioningService:
    def __init__(self) -> None:
        self.tenant_repository = TenantRepository()
        self.profile_repository = TenantProfileRepository()
        self.settings_repository = TenantSettingsRepository()
        self.subscription_repository = TenantSubscriptionRepository()
        self.domain_repository = TenantDomainRepository()
        self.role_bootstrap_service = RoleBootstrapService()
        self.assignment_service = RoleAssignmentService()

    @transaction.atomic
    def provision_tenant(
        self,
        *,
        name: str,
        code: str | None = None,
        slug: str | None = None,
        legal_name: str | None = None,
        admin_email: str | None = None,
        admin_password: str | None = None,
        admin_first_name: str = "Admin",
        admin_last_name: str = "User",
        owner_id: str | None = None,
        plan: str = SubscriptionPlan.TRIAL,
        billing_cycle: str = BillingCycle.MONTHLY,
        country: str = "Yemen",
        currency: str = "YER",
        timezone_str: str = "UTC",
        custom_domain: str | None = None,
    ):
        clean_slug = slugify(slug or name)
        if not clean_slug:
            clean_slug = f"tenant-{timezone.now().strftime('%Y%m%d%H%M%S')}"

        if self.tenant_repository.exists(slug=clean_slug):
            raise DuplicateSlugError(f"A tenant with slug '{clean_slug}' already exists.", field="slug")

        clean_code = (code or clean_slug).lower().replace("-", "_")
        if self.tenant_repository.exists(code=clean_code):
            raise DuplicateSlugError(f"A tenant with code '{clean_code}' already exists.", field="code")

        # 1. Create Core Tenant
        tenant = self.tenant_repository.create(
            name=name,
            code=clean_code,
            slug=clean_slug,
            timezone=timezone_str,
            subscription_tier=plan,
            is_active=True,
        )

        # 2. Create Profile
        self.profile_repository.create(
            tenant=tenant,
            legal_name=legal_name or name,
            display_name=name,
            country=country,
            currency=currency,
            timezone=timezone_str,
        )

        # 3. Create Settings
        self.settings_repository.create(tenant=tenant)

        # 4. Create Subscription
        quotas = PLAN_QUOTAS.get(plan, PLAN_QUOTAS[SubscriptionPlan.TRIAL])
        end_date = timezone.now() + timezone.timedelta(days=14 if plan == SubscriptionPlan.TRIAL else 30)
        self.subscription_repository.create(
            tenant=tenant,
            plan=plan,
            billing_cycle=billing_cycle,
            start_date=timezone.now(),
            end_date=end_date,
            is_trial=(plan == SubscriptionPlan.TRIAL),
            status=SubscriptionStatus.TRIALING if plan == SubscriptionPlan.TRIAL else SubscriptionStatus.ACTIVE,
            **quotas,
        )

        # 5. Create Primary Subdomain
        subdomain_name = f"{clean_slug}.pharmacloud.local"
        self.domain_repository.create(
            tenant=tenant,
            domain_name=subdomain_name,
            domain_type=DomainType.SUBDOMAIN,
            is_verified=True,
            is_primary=True,
        )

        if custom_domain:
            self.domain_repository.create(
                tenant=tenant,
                domain_name=custom_domain.lower().strip(),
                domain_type=DomainType.CUSTOM,
                is_verified=False,
                is_primary=False,
            )

        # 6. Bootstrap RBAC Roles (admin, member)
        self.role_bootstrap_service.ensure_tenant_defaults(tenant)

        # 7. Provision Owner / Admin User
        admin_user = None
        if owner_id:
            admin_user = User.objects.filter(pk=owner_id).first()

        if not admin_user and admin_email:
            import secrets

            admin_user = User.objects.filter(email=admin_email).first()
            if not admin_user:
                admin_user = User.objects.create_user(
                    email=admin_email,
                    first_name=admin_first_name,
                    last_name=admin_last_name,
                    password=admin_password or secrets.token_urlsafe(12),
                    email_verified=True,
                )

        if admin_user:
            admin_user.tenants.add(tenant)
            tenant.owner = admin_user
            tenant.save(update_fields=["owner", "updated_at"])

            # Assign Administrator role
            from apps.rbac.models import Role

            admin_role = Role.objects.filter(tenant=tenant, code="admin").first()
            if admin_role:
                self.assignment_service.assign(user=admin_user, role=admin_role, actor=None)

        logger.info("Successfully provisioned tenant %s (%s)", tenant.name, tenant.slug)
        return tenant
