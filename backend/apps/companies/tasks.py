"""Celery async tasks for Company Management."""

from __future__ import annotations

import logging

from celery import shared_task
from django.utils import timezone

from apps.companies.models import Company, CompanyStatus

logger = logging.getLogger(__name__)


@shared_task(name="apps.companies.tasks.audit_company_status_task")
def audit_company_status_task() -> int:
    """Routine task auditing company status records."""
    active_companies = Company.objects.filter(status=CompanyStatus.ACTIVE).count()
    logger.info("Company status audit complete; %d active companies found across platform", active_companies)
    return active_companies
