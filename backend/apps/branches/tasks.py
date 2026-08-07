"""Celery async tasks for Branch Management."""

from __future__ import annotations

import logging

from celery import shared_task

from apps.branches.models import Branch, BranchStatus

logger = logging.getLogger(__name__)


@shared_task(name="apps.branches.tasks.audit_branch_status_task")
def audit_branch_status_task() -> int:
    """Routine task auditing branch status across platform."""
    active_branches = Branch.objects.filter(status=BranchStatus.ACTIVE).count()
    logger.info("Branch status audit complete; %d active branches found across platform", active_branches)
    return active_branches
