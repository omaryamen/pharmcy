"""Comprehensive Test Suite for Enterprise SaaS Super Admin & Platform Operations Center (IMP-035 / apps.platform_ops)."""

import uuid
from decimal import Decimal
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.core.models import Tenant
from apps.platform_ops.models import (
    AlertCategory,
    AlertSeverity,
    GlobalFeatureFlag,
    HealthStatus,
    PlatformAlert,
    PlatformAuditLog,
    SystemHealthCheck,
    SystemMaintenanceWindow,
    TenantImpersonationLog,
)
from apps.platform_ops.selectors import (
    FeatureFlagSelector,
    PlatformOverviewSelector,
    SystemHealthSelector,
)
from apps.platform_ops.services import (
    MaintenanceModeService,
    TenantImpersonationService,
    TenantLifecycleAdminService,
)
from apps.saas.models import SaaSSubscription, SaaSSubscriptionStatus
from apps.saas.services import SubscriptionLifecycleService
from tests.test_saas import saas_setup

User = get_user_model()


@pytest.mark.django_db
class TestPlatformOverviewAndHealth:
    """Test suite for platform overview analytics and live system health diagnostics."""

    def test_platform_overview_selector(self):
        tenant, user, plan_starter, plan_pro = saas_setup()
        sub_service = SubscriptionLifecycleService()
        sub_service.create_subscription(tenant=tenant, plan_code=plan_starter.code, is_trial=False)

        # Create Platform Alert
        PlatformAlert.objects.create(
            severity=AlertSeverity.WARNING,
            category=AlertCategory.INFRASTRUCTURE,
            title="High CPU Usage",
            message="CPU utilization at 85%",
        )

        overview_selector = PlatformOverviewSelector()
        data = overview_selector.get_platform_overview()

        assert data["total_tenants"] >= 1
        assert data["active_tenants"] >= 1
        assert data["mrr"] == 50.0
        assert data["unresolved_platform_alerts"] >= 1
        assert data["is_maintenance_in_effect"] is False

    def test_system_health_selector_live_check(self):
        SystemHealthCheck.objects.create(
            component_name="PostgreSQL Primary",
            status=HealthStatus.HEALTHY,
            latency_ms=1.2,
        )

        health_selector = SystemHealthSelector()
        result = health_selector.perform_live_health_check()

        assert result["status"] == "healthy"
        assert result["database"]["status"] == HealthStatus.HEALTHY
        assert len(result["recent_checks"]) >= 1


@pytest.mark.django_db
class TestGlobalFeatureFlags:
    """Test suite for progressive rollout, whitelisting, and blacklisting in GlobalFeatureFlag."""

    def test_feature_flag_evaluation(self):
        tenant, user, plan_starter, plan_pro = saas_setup()
        selector = FeatureFlagSelector()

        # Flag 1: Whitelisted only
        GlobalFeatureFlag.objects.create(
            feature_key="ai_assistant_v2",
            name="AI Assistant v2",
            is_globally_enabled=False,
            whitelisted_tenants=[tenant.code],
        )

        assert selector.is_feature_enabled("ai_assistant_v2", tenant=tenant) is True

        # Flag 2: Blacklisted
        GlobalFeatureFlag.objects.create(
            feature_key="beta_pos_ui",
            name="Beta POS UI",
            is_globally_enabled=True,
            blacklisted_tenants=[tenant.code],
        )

        assert selector.is_feature_enabled("beta_pos_ui", tenant=tenant) is False

        # Flag 3: Unregistered flag
        assert selector.is_feature_enabled("unknown_feature", tenant=tenant) is False


@pytest.mark.django_db
class TestTenantLifecycleAdminService:
    """Test suite for super-admin tenant suspension, reactivation, and audit logs."""

    def test_suspend_and_reactivate_tenant(self):
        tenant, user, plan_starter, plan_pro = saas_setup()
        sub_service = SubscriptionLifecycleService()
        sub = sub_service.create_subscription(tenant=tenant, plan_code=plan_starter.code, is_trial=False)

        admin_service = TenantLifecycleAdminService()

        # Suspend Tenant
        admin_service.suspend_tenant(tenant, admin_user=user, reason="Non-payment of invoice")
        tenant.refresh_from_db()
        sub.refresh_from_db()

        assert tenant.is_active is False
        assert sub.status == SaaSSubscriptionStatus.SUSPENDED
        assert PlatformAuditLog.objects.filter(target_tenant=tenant, action="TENANT_SUSPENDED").exists()

        # Reactivate Tenant
        admin_service.reactivate_tenant(tenant, admin_user=user, reason="Payment received")
        tenant.refresh_from_db()
        sub.refresh_from_db()

        assert tenant.is_active is True
        assert sub.status == SaaSSubscriptionStatus.ACTIVE
        assert PlatformAuditLog.objects.filter(target_tenant=tenant, action="TENANT_REACTIVATED").exists()


@pytest.mark.django_db
class TestImpersonationAndMaintenance:
    """Test suite for Super Admin tenant impersonation and maintenance window management."""

    def test_tenant_impersonation_session(self):
        tenant, user, plan_starter, plan_pro = saas_setup()
        impersonation_service = TenantImpersonationService()

        log, token = impersonation_service.start_impersonation(
            admin_user=user,
            tenant=tenant,
            reason="Investigating billing issue",
            ticket_reference="TICK-1002",
        )

        assert log.admin_user == user
        assert log.impersonated_tenant == tenant
        assert token.startswith("imp_")
        assert log.ended_at is None

        # End Impersonation
        impersonation_service.end_impersonation(log.pk, actions_performed_count=3)
        log.refresh_from_db()
        assert log.ended_at is not None
        assert log.actions_count == 3

    def test_schedule_maintenance_window(self):
        maintenance_service = MaintenanceModeService()
        now = timezone.now()
        maint = maintenance_service.schedule_maintenance(
            title="Database Minor Upgrade",
            start_time=now,
            end_time=now + timezone.timedelta(hours=2),
            description="Upgrading Postgres minor version",
        )

        assert maint.is_active is True
        assert maint.is_currently_in_effect is True
        assert maint.bypass_key.startswith("maint_key_")
