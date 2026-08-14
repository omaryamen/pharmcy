"""NotificationSelector providing queries for user notification center and preferences."""

from __future__ import annotations

from typing import Any
from django.db.models import QuerySet

from apps.notifications.models import (
    Notification,
    NotificationPreference,
    NotificationStatus,
)


class NotificationSelector:
    """Selector layer managing queries for user notifications, unread counts, and preferences."""

    def get_unread_count(self, tenant: Any, user: Any) -> int:
        """Return total unread in-app notifications count for recipient user."""
        return Notification.objects.filter(
            tenant=tenant,
            recipient=user,
            read_at__isnull=True,
            status__in=[NotificationStatus.PENDING, NotificationStatus.SENT, NotificationStatus.DELIVERED],
        ).count()

    def get_user_notifications(
        self,
        tenant: Any,
        user: Any,
        *,
        status_filter: str | None = None,
        priority_filter: str | None = None,
    ) -> QuerySet[Notification]:
        """Fetch list of notifications for user with optional filters."""
        qs = Notification.objects.filter(tenant=tenant, recipient=user)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if priority_filter:
            qs = qs.filter(priority=priority_filter)
        return qs.order_by("-created_at")

    def get_user_preferences(self, tenant: Any, user: Any) -> QuerySet[NotificationPreference]:
        """Fetch active notification channel preferences for user."""
        return NotificationPreference.objects.filter(tenant=tenant, user=user)
