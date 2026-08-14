"""PlatformOverviewSelector aggregating high-level C-level platform metrics for Super Admin dashboard."""

from __future__ import annotations

from typing import Any
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.core.models import Tenant
from apps.platform_ops.models import PlatformAlert, SystemMaintenanceWindow
from apps.saas.selectors import SaaSAnalyticsSelector

User = get_user_model()


class PlatformOverviewSelector:
    """Selector calculating enterprise platform-wide aggregates across all tenants, users, and subscriptions."""

    def __init__(self, saas_analytics: SaaSAnalyticsSelector | None = None) -> None:
        self.saas_analytics = saas_analytics or SaaSAnalyticsSelector()

    def get_platform_overview(self) -> dict[str, Any]:
        """Aggregate total tenants, users, active subscriptions, platform MRR, active alerts, and maintenance windows."""
        total_tenants = Tenant.objects.count()
        active_tenants = Tenant.objects.filter(is_active=True).count()
        total_users = User.objects.filter(is_active=True).count()

        # SaaS Metrics
        saas_metrics = self.saas_analytics.get_saas_metrics_summary(currency="USD")

        # Unresolved Alerts
        unresolved_alerts_count = PlatformAlert.objects.filter(is_resolved=False).count()

        # Active Maintenance Window
        now = timezone.now()
        active_maint = SystemMaintenanceWindow.objects.filter(
            is_active=True,
            start_time__lte=now,
            end_time__gte=now,
        ).first()

        return {
            "total_tenants": total_tenants,
            "active_tenants": active_tenants,
            "total_active_users": total_users,
            "mrr": saas_metrics.get("mrr", 0.0),
            "arr": saas_metrics.get("arr", 0.0),
            "total_active_subscriptions": saas_metrics.get("total_active_subscriptions", 0),
            "unresolved_platform_alerts": unresolved_alerts_count,
            "is_maintenance_in_effect": active_maint is not None,
            "active_maintenance_title": active_maint.title if active_maint else None,
        }
