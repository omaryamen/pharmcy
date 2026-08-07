"""Tenant Subscription repository."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository
from apps.tenants.models import TenantSubscription


class TenantSubscriptionRepository(BaseRepository[TenantSubscription]):
    model = TenantSubscription

    def get_for_tenant(self, tenant) -> TenantSubscription | None:
        return self.get_or_none(tenant=tenant)
