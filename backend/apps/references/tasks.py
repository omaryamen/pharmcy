"""Celery async tasks for Enterprise Pharmaceutical Reference Data."""

from __future__ import annotations

import logging

from celery import shared_task

from apps.references.models import MedicineCategory

logger = logging.getLogger(__name__)


@shared_task(name="apps.references.tasks.audit_reference_data_task")
def audit_reference_data_task() -> int:
    """Routine task auditing active reference categories across platform."""
    category_count = MedicineCategory.objects.filter(is_active=True).count()
    logger.info("Reference data audit complete; %d active categories found across platform", category_count)
    return category_count
