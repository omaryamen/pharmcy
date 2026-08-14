"""EntitlementSelector calculating tenant feature entitlements and real-time database usage."""

from __future__ import annotations

import logging
from typing import Any
from django.contrib.auth import get_user_model
from django.db import models

from apps.branches.models import Branch
from apps.saas.exceptions import EntitlementExceededError
from apps.saas.models import PlanFeature, SaaSSubscription, SaaSSubscriptionStatus
from apps.warehouses.models import Warehouse

User = get_user_model()
logger = logging.getLogger(__name__)


class EntitlementSelector:
    """Selector layer verifying tenant entitlements, active subscription state, and database resource counts."""

    def get_active_subscription(self, tenant: Any) -> SaaSSubscription | None:
        """Fetch current active or trialing SaaS subscription for tenant."""
        return SaaSSubscription.objects.filter(
            tenant=tenant,
            status__in=[SaaSSubscriptionStatus.ACTIVE, SaaSSubscriptionStatus.TRIALING, SaaSSubscriptionStatus.GRACE_PERIOD],
        ).order_by("-created_at").first()

    def get_feature_limit(self, tenant: Any, feature_key: str) -> tuple[bool, int]:
        """Return (is_enabled, limit_value) for a given feature key on tenant's current plan version."""
        sub = self.get_active_subscription(tenant)
        if not sub or not sub.is_active_entitled:
            return False, 0

        feature = PlanFeature.objects.filter(
            plan_version=sub.plan_version,
            feature_key=feature_key,
        ).first()

        if not feature:
            # Default fallback for unconfigured boolean features
            return True, -1

        return feature.is_enabled, feature.limit_value

    def get_current_usage(self, tenant: Any, feature_key: str) -> int:
        """Calculate real-time resource count from database tables."""
        if feature_key == "max_users":
            count = User.objects.filter(
                models.Q(tenants=tenant) | models.Q(employee_profile__tenant=tenant) | models.Q(owned_tenants=tenant),
                is_active=True,
            ).distinct().count()
            return count if count > 0 else 1
        elif feature_key == "max_branches":
            return Branch.objects.filter(tenant=tenant, is_deleted=False).count()
        elif feature_key == "max_warehouses":
            return Warehouse.objects.filter(tenant=tenant, is_deleted=False).count()
        return 0

    def can_use_feature(self, tenant: Any, feature_key: str) -> bool:
        """Check if tenant has access to boolean or limit-based feature."""
        is_enabled, limit = self.get_feature_limit(tenant, feature_key)
        if not is_enabled:
            return False
        if limit == -1:
            return True

        current = self.get_current_usage(tenant, feature_key)
        return current < limit

    def check_limit_or_raise(self, tenant: Any, feature_key: str, requested_qty: int = 1) -> None:
        """Enforce limit check and raise EntitlementExceededError if tenant exceeds quota."""
        is_enabled, limit = self.get_feature_limit(tenant, feature_key)
        if not is_enabled:
            raise EntitlementExceededError(feature_key, 0, 1)
        if limit == -1:
            return

        current = self.get_current_usage(tenant, feature_key)
        if current + requested_qty > limit:
            raise EntitlementExceededError(feature_key, limit, current + requested_qty)
