"""Celery async tasks for Enterprise User Management."""

from __future__ import annotations

import logging

from celery import shared_task
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(name="apps.users.tasks.audit_user_account_status_task")
def audit_user_account_status_task() -> int:
    """Routine task auditing active vs locked user accounts."""
    active_users = User.objects.filter(is_active=True).count()
    logger.info("User status audit complete; %d active users found across platform", active_users)
    return active_users
