"""Celery tasks for Enterprise Supplier Management background jobs."""

from __future__ import annotations

import logging

from celery import shared_task
from django.utils import timezone

from apps.suppliers.models import Supplier

logger = logging.getLogger(__name__)


@shared_task
def audit_supplier_license_expirations() -> dict[str, int]:
    """Background job auditing suppliers with expired drug or commercial licenses."""
    today = timezone.now().date()
    expired_suppliers = Supplier.objects.filter(
        is_deleted=False,
        license_expiry_date__lt=today,
        status="active",
    )
    count = expired_suppliers.count()
    logger.info("Supplier license audit complete. %d active suppliers have expired licenses.", count)
    return {"expired_count": count}
