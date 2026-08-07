"""Tenant subscription and quota enforcement service."""

from __future__ import annotations

import logging

from django.db import transaction
from django.utils import timezone

from apps.tenants.exceptions import TenantLimitExceededError
from apps.tenants.models import SubscriptionPlan, SubscriptionStatus
from apps.tenants.repositories import TenantSubscriptionRepository
from apps.tenants.services.provisioning import PLAN_QUOTAS

logger = logging.getLogger(__name__)


class TenantSubscriptionService:
    def __init__(self) -> None:
        self.subscription_repository = TenantSubscriptionRepository()

    @transaction.atomic
    def update_subscription(
        self,
        tenant,
        *,
        plan: str,
        billing_cycle: str | None = None,
        extend_days: int = 30,
        custom_quotas: dict | None = None,
    ):
        subscription = self.subscription_repository.get_for_tenant(tenant)
        quotas = PLAN_QUOTAS.get(plan, PLAN_QUOTAS[SubscriptionPlan.TRIAL])

        if custom_quotas:
            quotas = {**quotas, **custom_quotas}

        subscription.plan = plan
        if billing_cycle:
            subscription.billing_cycle = billing_cycle

        subscription.is_trial = (plan == SubscriptionPlan.TRIAL)
        subscription.status = SubscriptionStatus.ACTIVE if plan != SubscriptionPlan.TRIAL else SubscriptionStatus.TRIALING
        subscription.end_date = timezone.now() + timezone.timedelta(days=extend_days)

        for q_key, q_val in quotas.items():
            if hasattr(subscription, q_key):
                setattr(subscription, q_key, q_val)

        subscription.save()
        tenant.subscription_tier = plan
        tenant.save(update_fields=["subscription_tier", "updated_at"])

        logger.info("Updated subscription for tenant %s to plan %s", tenant.slug, plan)
        return subscription

    def check_user_quota(self, tenant, requested_addition: int = 1) -> None:
        subscription = getattr(tenant, "subscription", None)
        if not subscription:
            return
        current_users_count = tenant.users.count()
        if current_users_count + requested_addition > subscription.max_users:
            raise TenantLimitExceededError(
                f"Tenant user quota limit reached ({subscription.max_users} max users allowed).",
                field="users_limit",
            )

    def check_branch_quota(self, tenant, current_branch_count: int, requested_addition: int = 1) -> None:
        subscription = getattr(tenant, "subscription", None)
        if not subscription:
            return
        if current_branch_count + requested_addition > subscription.max_branches:
            raise TenantLimitExceededError(
                f"Tenant branch quota limit reached ({subscription.max_branches} max branches allowed).",
                field="branches_limit",
            )
