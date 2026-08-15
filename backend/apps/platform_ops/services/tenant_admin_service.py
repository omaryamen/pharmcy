"""TenantLifecycleAdminService executing high-privilege super-admin tenant management operations."""

from __future__ import annotations

import logging
from typing import Any
from django.db import transaction
from django.utils import timezone

from apps.core.models import Tenant
from apps.platform_ops.models import PlatformAuditLog
from apps.saas.models import SaaSSubscription, SaaSSubscriptionStatus

logger = logging.getLogger(__name__)


class TenantLifecycleAdminService:
    """Service layer managing super-admin tenant operations (suspension, reactivation, quota overrides)."""

    @transaction.atomic
    def suspend_tenant(
        self,
        tenant: Tenant,
        *,
        admin_user: Any,
        reason: str,
        ip_address: str | None = None,
    ) -> None:
        """Suspend customer tenant and its active SaaS subscriptions."""
        tenant.is_active = False
        tenant.save(update_fields=["is_active", "updated_at"])

        # Update active SaaS subscriptions to SUSPENDED
        SaaSSubscription.objects.filter(
            tenant=tenant,
            status__in=[SaaSSubscriptionStatus.ACTIVE, SaaSSubscriptionStatus.TRIALING, SaaSSubscriptionStatus.GRACE_PERIOD],
        ).update(status=SaaSSubscriptionStatus.SUSPENDED, updated_at=timezone.now())

        PlatformAuditLog.objects.create(
            actor=admin_user,
            action="TENANT_SUSPENDED",
            target_tenant=tenant,
            target_object_type="Tenant",
            target_object_id=str(tenant.pk),
            description=f"Tenant '{tenant.name}' suspended by Admin. Reason: {reason}",
            ip_address=ip_address,
        )
        logger.warning("Super Admin %s suspended Tenant %s. Reason: %s", admin_user, tenant.name, reason)

    @transaction.atomic
    def reactivate_tenant(
        self,
        tenant: Tenant,
        *,
        admin_user: Any,
        reason: str,
        ip_address: str | None = None,
    ) -> None:
        """Reactivate customer tenant and restore its subscriptions."""
        tenant.is_active = True
        tenant.save(update_fields=["is_active", "updated_at"])

        # Restore suspended subscriptions to ACTIVE
        SaaSSubscription.objects.filter(
            tenant=tenant,
            status=SaaSSubscriptionStatus.SUSPENDED,
        ).update(status=SaaSSubscriptionStatus.ACTIVE, updated_at=timezone.now())

        PlatformAuditLog.objects.create(
            actor=admin_user,
            action="TENANT_REACTIVATED",
            target_tenant=tenant,
            target_object_type="Tenant",
            target_object_id=str(tenant.pk),
            description=f"Tenant '{tenant.name}' reactivated by Admin. Reason: {reason}",
            ip_address=ip_address,
        )
        logger.info("Super Admin %s reactivated Tenant %s. Reason: %s", admin_user, tenant.name, reason)
