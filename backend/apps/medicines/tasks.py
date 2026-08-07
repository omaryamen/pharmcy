"""Celery async tasks for Enterprise Medicine Master Data."""

from __future__ import annotations

import logging

from celery import shared_task

from apps.medicines.models import Medicine, MedicineStatus

logger = logging.getLogger(__name__)


@shared_task(name="apps.medicines.tasks.audit_medicine_catalog_task")
def audit_medicine_catalog_task() -> int:
    """Routine task auditing active medicine catalog records."""
    active_count = Medicine.objects.filter(status=MedicineStatus.ACTIVE).count()
    logger.info("Medicine master catalog audit complete; %d active medicines found across platform", active_count)
    return active_count
