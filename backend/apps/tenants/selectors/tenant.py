"""Tenant selector functions for optimized read queries and statistics."""

from __future__ import annotations

from typing import Any

from django.db.models import Count, QuerySet

from apps.core.models import Tenant
from apps.tenants.repositories import TenantRepository


class TenantSelector:
    def __init__(self) -> None:
        self.repository = TenantRepository()

    def list_tenants(self, *, status: str | None = None, search: str | None = None) -> QuerySet[Tenant]:
        qs = self.repository.get_queryset().select_related("profile", "subscription", "owner")
        if status:
            qs = qs.filter(status=status)
        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(slug__icontains=search)
        return qs

    def get_tenant_detail(self, tenant_id) -> Tenant | None:
        return self.repository.get_with_details(tenant_id)

    def get_tenant_stats(self, tenant: Tenant) -> dict[str, Any]:
        subscription = getattr(tenant, "subscription", None)
        user_count = tenant.users.count()
        domains_count = tenant.domains.count()

        max_users = subscription.max_users if subscription else 5
        max_branches = subscription.max_branches if subscription else 1
        storage_limit_mb = subscription.storage_limit_mb if subscription else 1024

        return {
            "tenant_id": str(tenant.pk),
            "name": tenant.name,
            "slug": tenant.slug,
            "status": tenant.status,
            "user_count": user_count,
            "domains_count": domains_count,
            "quota_usage": {
                "users": {"used": user_count, "limit": max_users, "percentage": round((user_count / max_users) * 100, 2)},
                "branches": {"used": 1, "limit": max_branches, "percentage": round((1 / max_branches) * 100, 2)},
                "storage_mb": {"used": 15, "limit": storage_limit_mb, "percentage": round((15 / storage_limit_mb) * 100, 2)},
            },
        }
