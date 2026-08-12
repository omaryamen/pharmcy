"""CashSessionReconciliationService managing POS cashier shift closing, till cash counting, and variance recording."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.cash_and_bank.exceptions import CashSessionAlreadyClosedError
from apps.cash_and_bank.models import CashVariance, VarianceType
from apps.cash_and_bank.services.number_generator import TreasuryNumberGenerator
from apps.sales.models import CashRegister, RegisterSession, SessionStatus

logger = logging.getLogger(__name__)


class CashSessionReconciliationService:
    """Service layer executing POS cash session closing, actual till count reconciliation, and cash variance logging."""

    def __init__(self, number_generator: TreasuryNumberGenerator | None = None) -> None:
        self.number_generator = number_generator or TreasuryNumberGenerator()

    @transaction.atomic
    def close_and_reconcile_cash_session(
        self,
        tenant: Any,
        session: RegisterSession,
        actual_closing_cash: Decimal | float | int,
        *,
        reason: str = "",
        user: Any | None = None,
    ) -> tuple[RegisterSession, CashVariance | None]:
        """Close POS cashier shift session, reconcile expected vs actual cash, and record cash variances."""
        sess = RegisterSession.objects.select_for_update().get(pk=session.pk, tenant=tenant)
        register = CashRegister.objects.select_for_update().get(pk=sess.cash_register.pk, tenant=tenant)

        if sess.status == SessionStatus.CLOSED:
            raise CashSessionAlreadyClosedError(f"Register session {sess.session_number} is already closed.")

        actual_cash = Decimal(str(actual_closing_cash))
        expected_cash = sess.expected_cash
        variance_amount = actual_cash - expected_cash

        variance_record = None

        if variance_amount != Decimal("0.0000"):
            v_type = VarianceType.OVERAGE if variance_amount > Decimal("0.0000") else VarianceType.SHORTAGE
            cvr_num = self.number_generator.generate_variance_number(tenant)

            variance_record = CashVariance.objects.create(
                tenant=tenant,
                register_session=sess,
                variance_number=cvr_num,
                variance_type=v_type,
                expected_amount=expected_cash,
                actual_amount=actual_cash,
                variance_amount=abs(variance_amount),
                reason=reason,
                status="pending",
                created_by=user,
            )
            sess.status = SessionStatus.CLOSED
            sess.notes = f"Closed with variance: {v_type} of ${abs(variance_amount)}"
        else:
            sess.status = SessionStatus.CLOSED

        now = timezone.now()
        sess.actual_cash = actual_cash
        sess.variance = variance_amount
        sess.closed_at = now
        sess.save()

        register.status = "closed"
        register.save(update_fields=["status", "updated_at"])

        logger.info(f"Closed RegisterSession {sess.session_number} (Expected: ${expected_cash}, Actual: ${actual_cash}, Variance: ${variance_amount})")
        return sess, variance_record
