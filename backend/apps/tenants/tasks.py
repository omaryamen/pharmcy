"""Celery async tasks for Tenant lifecycle and maintenance."""

from __future__ import annotations

import logging

from celery import shared_task
from django.utils import timezone

from apps.core.models import Tenant, TenantStatus
from apps.tenants.models import SubscriptionStatus, TenantSubscription

logger = logging.getLogger(__name__)


@shared_task(name="apps.tenants.tasks.check_subscription_expirations_task")
def check_subscription_expirations_task() -> int:
    """Check for expired tenant subscriptions and transition status."""
    now = timezone.now()
    expired_subs = TenantSubscription.objects.filter(
        status__in=[SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING],
        end_date__lt=now,
    )
    count = 0
    for sub in expired_subs:
        sub.status = SubscriptionStatus.EXPIRED
        sub.save(update_fields=["status", "updated_at"])

        tenant = sub.tenant
        tenant.status = TenantStatus.SUSPENDED
        tenant.is_active = False
        tenant.save(update_fields=["status", "is_active", "updated_at"])
        count += 1

    logger.info("Checked subscription expirations; marked %d tenants as expired/suspended", count)
    return count


@shared_task(name="apps.tenants.tasks.cleanup_archived_tenants_task")
def cleanup_archived_tenants_task() -> int:
    """Routine task logging long-term archived tenants."""
    cutoff = timezone.now() - timezone.timedelta(days=365)
    archived_count = Tenant.objects.filter(status=TenantStatus.ARCHIVED, updated_at__lt=cutoff).count()
    logger.info("Found %d archived tenants older than 1 year", archived_count)
    return archived_count
