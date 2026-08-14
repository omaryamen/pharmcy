"""SubscriptionLifecycleService managing tenant subscription lifecycle, license issuance, and IMP-033 events."""

from __future__ import annotations

import logging
import uuid
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.notifications.services import EventPublisherService
from apps.saas.exceptions import SubscriptionStateError
from apps.saas.models import (
    Plan,
    PlanVersion,
    SaaSBillingCycle,
    SaaSInvoice,
    SaaSInvoiceLine,
    SaaSInvoiceStatus,
    SaaSLicense,
    SaaSLicenseStatus,
    SaaSLicenseType,
    SaaSLineItemType,
    SaaSSubscription,
    SaaSSubscriptionStatus,
)
from apps.saas.services.number_generator import SaaSNumberGenerator
from apps.saas.services.proration_service import ProrationCalculatorService
from apps.tenants.models import TenantSubscription, SubscriptionStatus as LegacySubStatus

logger = logging.getLogger(__name__)


class SubscriptionLifecycleService:
    """Service layer managing subscription provisioning, upgrades, downgrades, renewals, and cancellations."""

    def __init__(
        self,
        number_generator: SaaSNumberGenerator | None = None,
        proration_calculator: ProrationCalculatorService | None = None,
        event_publisher: EventPublisherService | None = None,
    ) -> None:
        self.number_generator = number_generator or SaaSNumberGenerator()
        self.proration_calculator = proration_calculator or ProrationCalculatorService()
        self.event_publisher = event_publisher or EventPublisherService()

    @transaction.atomic
    def create_subscription(
        self,
        tenant: Any,
        plan_code: str,
        *,
        billing_cycle: str = SaaSBillingCycle.MONTHLY,
        currency: str = "USD",
        is_trial: bool = True,
        actor: Any | None = None,
    ) -> SaaSSubscription:
        """Create a new commercial SaaS subscription, license key, and sync legacy TenantSubscription."""
        plan = Plan.objects.get(code=plan_code, is_active=True)
        version = PlanVersion.objects.get(plan=plan, is_current=True)

        now = timezone.now()
        sub_num = self.number_generator.generate_subscription_number(tenant)

        trial_end = now + timezone.timedelta(days=14) if is_trial else None
        period_end = trial_end if is_trial else (now + timezone.timedelta(days=30 if billing_cycle == SaaSBillingCycle.MONTHLY else 365))
        status = SaaSSubscriptionStatus.TRIALING if is_trial else SaaSSubscriptionStatus.ACTIVE

        sub = SaaSSubscription.objects.create(
            tenant=tenant,
            subscription_number=sub_num,
            plan=plan,
            plan_version=version,
            status=status,
            billing_cycle=billing_cycle,
            currency=currency,
            start_date=now,
            trial_start=now if is_trial else None,
            trial_end=trial_end,
            current_period_start=now,
            current_period_end=period_end,
            next_billing_date=period_end,
        )

        # Issue SaaSLicense
        lic_num = self.number_generator.generate_license_number(tenant)
        lic_key = f"LIC-KEY-{tenant.code}-{uuid.uuid4().hex[:12].upper()}"
        SaaSLicense.objects.create(
            tenant=tenant,
            subscription=sub,
            license_number=lic_num,
            license_key=lic_key,
            license_type=SaaSLicenseType.TRIAL if is_trial else SaaSLicenseType.SUBSCRIPTION,
            status=SaaSLicenseStatus.TRIAL if is_trial else SaaSLicenseStatus.ACTIVE,
            expires_at=period_end,
        )

        # Sync legacy TenantSubscription model in apps.tenants
        TenantSubscription.objects.update_or_create(
            tenant=tenant,
            defaults={
                "plan": plan_code if plan_code in ["trial", "starter", "professional", "enterprise"] else "professional",
                "billing_cycle": billing_cycle,
                "is_trial": is_trial,
                "status": LegacySubStatus.TRIALING if is_trial else LegacySubStatus.ACTIVE,
                "start_date": now,
                "end_date": period_end,
            },
        )

        # Publish IMP-033 Domain Event
        self.event_publisher.publish_event(
            tenant=tenant,
            event_type="subscription.created",
            source_module="saas",
            source_object_id=sub.subscription_number,
            payload={"subscription_number": sub.subscription_number, "plan": plan_code, "status": status},
            actor=actor,
        )

        logger.info("Created SaaS Subscription %s for Tenant %s", sub_num, tenant.name)
        return sub

    @transaction.atomic
    def upgrade_subscription(
        self,
        subscription: SaaSSubscription,
        new_plan_code: str,
        *,
        actor: Any | None = None,
    ) -> SaaSInvoice:
        """Upgrade subscription to a higher plan version, calculate proration, and issue invoice."""
        new_plan = Plan.objects.get(code=new_plan_code, is_active=True)
        new_version = PlanVersion.objects.get(plan=new_plan, is_current=True)

        price_obj = new_version.prices.filter(billing_cycle=subscription.billing_cycle, currency=subscription.currency).first()
        new_price = price_obj.price_amount if price_obj else Decimal("0.0000")

        unused_credit, new_charge, net_due = self.proration_calculator.calculate_proration(subscription, new_price)

        # Update Subscription Plan & Version
        subscription.plan = new_plan
        subscription.plan_version = new_version
        subscription.status = SaaSSubscriptionStatus.ACTIVE
        subscription.save(update_fields=["plan", "plan_version", "status", "updated_at"])

        # Update SaaSLicense
        if hasattr(subscription, "license"):
            subscription.license.status = SaaSLicenseStatus.ACTIVE
            subscription.license.save(update_fields=["status", "updated_at"])

        # Create Prorated Invoice
        inv_num = self.number_generator.generate_invoice_number(subscription.tenant)
        now = timezone.now()
        invoice = SaaSInvoice.objects.create(
            tenant=subscription.tenant,
            subscription=subscription,
            invoice_number=inv_num,
            billing_period_start=subscription.current_period_start,
            billing_period_end=subscription.current_period_end,
            issue_date=now.date(),
            due_date=now.date(),
            subtotal=new_charge,
            discount_amount=unused_credit,
            total_amount=net_due,
            currency=subscription.currency,
            status=SaaSInvoiceStatus.OPEN,
        )

        SaaSInvoiceLine.objects.create(
            tenant=subscription.tenant,
            invoice=invoice,
            line_type=SaaSLineItemType.PLAN_FEE,
            description=f"Upgrade to Plan {new_plan.name}",
            quantity=1,
            unit_price=new_charge,
            amount=new_charge,
            currency=subscription.currency,
        )

        if unused_credit > 0:
            SaaSInvoiceLine.objects.create(
                tenant=subscription.tenant,
                invoice=invoice,
                line_type=SaaSLineItemType.PRORATION_CREDIT,
                description="Proration Credit for Previous Plan",
                quantity=1,
                unit_price=-unused_credit,
                amount=-unused_credit,
                currency=subscription.currency,
            )

        self.event_publisher.publish_event(
            tenant=subscription.tenant,
            event_type="subscription.upgraded",
            source_module="saas",
            source_object_id=subscription.subscription_number,
            payload={"subscription_number": subscription.subscription_number, "new_plan": new_plan_code, "invoice": inv_num},
            actor=actor,
        )

        logger.info("Upgraded Subscription %s to Plan %s", subscription.subscription_number, new_plan_code)
        return invoice
