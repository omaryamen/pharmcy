"""ReceivableDisputeService managing customer invoice disputes and resolution workflows."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.accounts_receivable.models import (
    ARStatus,
    CustomerReceivable,
    DisputeReason,
    DisputeStatus,
    ReceivableDispute,
)
from apps.accounts_receivable.services.number_generator import ARNumberGenerator

logger = logging.getLogger(__name__)


class ReceivableDisputeService:
    """Service layer managing customer receivable dispute registration and financial resolution."""

    def __init__(self, number_generator: ARNumberGenerator | None = None) -> None:
        self.number_generator = number_generator or ARNumberGenerator()

    @transaction.atomic
    def log_dispute(
        self,
        tenant: Any,
        receivable: CustomerReceivable,
        dispute_amount: Decimal | float | int,
        reason: str = DisputeReason.WRONG_AMOUNT,
        description: str = "",
        user: Any | None = None,
    ) -> ReceivableDispute:
        """Register a formal customer receivable invoice dispute."""
        rx = CustomerReceivable.objects.select_for_update().get(pk=receivable.pk, tenant=tenant)
        dsp_num = self.number_generator.generate_dispute_number(tenant)

        dispute = ReceivableDispute.objects.create(
            tenant=tenant,
            receivable=rx,
            dispute_number=dsp_num,
            dispute_amount=Decimal(str(dispute_amount)),
            reason=reason,
            status=DisputeStatus.OPEN,
            description=description,
            created_by=user,
        )

        rx.status = ARStatus.DISPUTED
        rx.save(update_fields=["status", "updated_at"])

        logger.info(f"Logged ReceivableDispute {dsp_num} for receivable {rx.receivable_number}")
        return dispute

    @transaction.atomic
    def resolve_dispute(
        self,
        tenant: Any,
        dispute: ReceivableDispute,
        resolution_status: str,
        resolution_notes: str,
        reviewer: Any,
    ) -> ReceivableDispute:
        """Resolve a customer receivable dispute."""
        dsp = ReceivableDispute.objects.select_for_update().get(pk=dispute.pk, tenant=tenant)
        rx = CustomerReceivable.objects.select_for_update().get(pk=dsp.receivable.pk, tenant=tenant)

        dsp.status = resolution_status
        dsp.resolution_notes = resolution_notes
        dsp.reviewed_by = reviewer
        dsp.resolved_at = timezone.now()
        dsp.save(update_fields=["status", "resolution_notes", "reviewed_by", "resolved_at", "updated_at"])

        rx.recalculate_balances()
        rx.save(update_fields=["status", "updated_at"])

        logger.info(f"Resolved ReceivableDispute {dsp.dispute_number} as {resolution_status}")
        return dsp
