"""TenantImpersonationService managing secure, auditable tenant impersonation sessions for Super Admins."""

from __future__ import annotations

import logging
import uuid
from typing import Any
from django.utils import timezone

from apps.core.models import Tenant
from apps.platform_ops.models import TenantImpersonationLog

logger = logging.getLogger(__name__)


class TenantImpersonationService:
    """Service layer initiating and tracking auditable Super Admin customer support sessions."""

    def start_impersonation(
        self,
        admin_user: Any,
        tenant: Tenant,
        reason: str,
        *,
        ticket_reference: str = "",
        ip_address: str | None = None,
    ) -> tuple[TenantImpersonationLog, str]:
        """Initiate impersonation session, log audit record, and generate scoped impersonation session token."""
        log = TenantImpersonationLog.objects.create(
            admin_user=admin_user,
            impersonated_tenant=tenant,
            reason=reason,
            ticket_reference=ticket_reference,
            started_at=timezone.now(),
            ip_address=ip_address,
        )

        impersonation_token = f"imp_{admin_user.pk}_{tenant.pk}_{uuid.uuid4().hex}"
        logger.warning(
            "Super Admin %s started impersonation session for Tenant %s (Log ID: %s, Ticket: %s)",
            admin_user,
            tenant.name,
            log.pk,
            ticket_reference,
        )
        return log, impersonation_token

    def end_impersonation(self, log_id: str | int, actions_performed_count: int = 0) -> None:
        """Mark impersonation session as ended."""
        log = TenantImpersonationLog.objects.filter(pk=log_id).first()
        if log and not log.ended_at:
            log.ended_at = timezone.now()
            log.actions_count = actions_performed_count
            log.save(update_fields=["ended_at", "actions_count", "updated_at"])
