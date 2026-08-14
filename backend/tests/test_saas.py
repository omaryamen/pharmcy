"""Comprehensive Test Suite for Enterprise SaaS Subscription, Billing & Licensing Platform (IMP-034 / apps.saas)."""

import uuid
from decimal import Decimal
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.core.models import Tenant
from apps.saas.exceptions import EntitlementExceededError
from apps.saas.models import (
    Plan,
    PlanFeature,
    PlanPrice,
    PlanVersion,
    SaaSBillingCycle,
    SaaSInvoice,
    SaaSInvoiceStatus,
    SaaSLicense,
    SaaSLicenseStatus,
    SaaSPayment,
    SaaSPaymentStatus,
    SaaSSubscription,
    SaaSSubscriptionStatus,
)
from apps.saas.selectors import EntitlementSelector, SaaSAnalyticsSelector
from apps.saas.services import ProrationCalculatorService, SaaSPaymentService, SubscriptionLifecycleService

User = get_user_model()


def saas_setup():
    """Helper setup creating tenant, plans, plan versions, prices, and features."""
    uid = uuid.uuid4().hex[:6]
    tenant = Tenant.objects.create(name=f"SaaS Tenant {uid}", code=f"TNT-{uid}", slug=f"saas-slug-{uid}")
    user = User.objects.create_user(email=f"user_{uid}@test.com", first_name="SaaS", last_name="Admin", password="pass")
    tenant.owner = user
    tenant.save(update_fields=["owner"])

    # Plan 1: Starter
    plan_starter = Plan.objects.create(code=f"starter_{uid}", name="Starter Plan", is_active=True, is_public=True)
    ver_starter = PlanVersion.objects.create(plan=plan_starter, version_number=1, is_current=True)
    PlanPrice.objects.create(plan_version=ver_starter, billing_cycle=SaaSBillingCycle.MONTHLY, currency="USD", price_amount=Decimal("50.0000"))
    PlanFeature.objects.create(plan_version=ver_starter, feature_key="max_users", feature_name="Max Users", is_enabled=True, limit_value=3)
    PlanFeature.objects.create(plan_version=ver_starter, feature_key="max_branches", feature_name="Max Branches", is_enabled=True, limit_value=1)

    # Plan 2: Professional
    plan_pro = Plan.objects.create(code=f"pro_{uid}", name="Professional Plan", is_active=True, is_public=True)
    ver_pro = PlanVersion.objects.create(plan=plan_pro, version_number=1, is_current=True)
    PlanPrice.objects.create(plan_version=ver_pro, billing_cycle=SaaSBillingCycle.MONTHLY, currency="USD", price_amount=Decimal("150.0000"))
    PlanFeature.objects.create(plan_version=ver_pro, feature_key="max_users", feature_name="Max Users", is_enabled=True, limit_value=10)
    PlanFeature.objects.create(plan_version=ver_pro, feature_key="max_branches", feature_name="Max Branches", is_enabled=True, limit_value=5)

    return tenant, user, plan_starter, plan_pro


@pytest.mark.django_db
class TestSubscriptionLifecycleAndLicensing:
    """Test suite for subscription creation, trial period, and license key generation."""

    def test_create_subscription_issues_license(self):
        tenant, user, plan_starter, plan_pro = saas_setup()
        service = SubscriptionLifecycleService()

        sub = service.create_subscription(
            tenant=tenant,
            plan_code=plan_starter.code,
            billing_cycle=SaaSBillingCycle.MONTHLY,
            is_trial=True,
            actor=user,
        )

        assert sub.subscription_number.startswith("SUB-")
        assert sub.status == SaaSSubscriptionStatus.TRIALING
        assert hasattr(sub, "license")
        assert sub.license.license_key.startswith("LIC-KEY-")
        assert sub.license.status == SaaSLicenseStatus.TRIAL

    def test_entitlement_selector_limit_enforcement(self):
        tenant, user, plan_starter, plan_pro = saas_setup()
        service = SubscriptionLifecycleService()
        selector = EntitlementSelector()

        sub = service.create_subscription(tenant=tenant, plan_code=plan_starter.code, is_trial=False)

        # Tenant currently has 1 user (user) against limit of 3
        can_add_user = selector.can_use_feature(tenant, "max_users")
        assert can_add_user is True

        # Check limit or raise does not raise when within limit
        selector.check_limit_or_raise(tenant, "max_users", requested_qty=1)

        # Check limit or raise raises EntitlementExceededError when requesting more than allowed
        with pytest.raises(EntitlementExceededError):
            selector.check_limit_or_raise(tenant, "max_users", requested_qty=3)


@pytest.mark.django_db
class TestProrationAndUpgrades:
    """Test suite for plan upgrade and proration calculation."""

    def test_upgrade_subscription_calculates_proration_and_issues_invoice(self):
        tenant, user, plan_starter, plan_pro = saas_setup()
        service = SubscriptionLifecycleService()

        sub = service.create_subscription(tenant=tenant, plan_code=plan_starter.code, is_trial=False)

        # Upgrade to Professional
        invoice = service.upgrade_subscription(sub, plan_pro.code, actor=user)
        sub.refresh_from_db()

        assert sub.plan == plan_pro
        assert invoice.invoice_number.startswith("SINV-")
        assert invoice.status == SaaSInvoiceStatus.OPEN
        assert invoice.total_amount > Decimal("0.0000")


@pytest.mark.django_db
class TestSaaSPaymentProcessingAndGL:
    """Test suite for SaaS invoice payment settlement, GL posting, and refunds."""

    def test_process_invoice_payment_settles_invoice(self):
        tenant, user, plan_starter, plan_pro = saas_setup()
        sub_service = SubscriptionLifecycleService()
        pay_service = SaaSPaymentService()

        sub = sub_service.create_subscription(tenant=tenant, plan_code=plan_starter.code, is_trial=False)
        invoice = sub_service.upgrade_subscription(sub, plan_pro.code)

        payment = pay_service.process_invoice_payment(invoice, actor=user)
        invoice.refresh_from_db()

        assert payment.payment_number.startswith("SPAY-")
        assert payment.status == SaaSPaymentStatus.SUCCEEDED
        assert invoice.status == SaaSInvoiceStatus.PAID

    def test_process_payment_refund(self):
        tenant, user, plan_starter, plan_pro = saas_setup()
        sub_service = SubscriptionLifecycleService()
        pay_service = SaaSPaymentService()

        sub = sub_service.create_subscription(tenant=tenant, plan_code=plan_starter.code, is_trial=False)
        invoice = sub_service.upgrade_subscription(sub, plan_pro.code)
        payment = pay_service.process_invoice_payment(invoice)

        refund = pay_service.process_refund(payment, refund_amount=payment.amount, reason="Customer request")
        payment.refresh_from_db()

        assert refund.refund_number.startswith("SRFD-")
        assert payment.status == SaaSPaymentStatus.REFUNDED


@pytest.mark.django_db
class TestSaaSAnalyticsAndTenantIsolation:
    """Test suite for SaaS MRR/ARR analytics and tenant isolation."""

    def test_saas_analytics_summary(self):
        tenant, user, plan_starter, plan_pro = saas_setup()
        sub_service = SubscriptionLifecycleService()

        sub_service.create_subscription(tenant=tenant, plan_code=plan_starter.code, is_trial=False)

        analytics = SaaSAnalyticsSelector()
        metrics = analytics.get_saas_metrics_summary(currency="USD")

        assert metrics["currency"] == "USD"
        assert metrics["total_active_subscriptions"] == 1
        assert metrics["mrr"] == 50.0

    def test_saas_tenant_isolation(self):
        tenant1, user1, plan1, _ = saas_setup()
        uid2 = uuid.uuid4().hex[:6]
        tenant2 = Tenant.objects.create(name=f"SaaS Tenant 2 {uid2}", code=f"TNT-{uid2}", slug=f"saas-slug-2-{uid2}")

        sub_service = SubscriptionLifecycleService()
        sub1 = sub_service.create_subscription(tenant=tenant1, plan_code=plan1.code, is_trial=False)

        selector = EntitlementSelector()
        t1_sub = selector.get_active_subscription(tenant1)
        t2_sub = selector.get_active_subscription(tenant2)

        assert t1_sub.pk == sub1.pk
        assert t2_sub is None
