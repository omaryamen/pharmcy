"""ReceivableAdjustmentService managing credit/debit adjustments and bad debt write-offs."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction

from apps.accounts_receivable.models import (
    ARAdjustmentStatus,
    ARAdjustmentType,
    ARStatus,
    CustomerReceivable,
    ReceivableAdjustment,
    ReceivableWriteOff,
)
from apps.accounts_receivable.services.number_generator import ARNumberGenerator
from apps.accounts_receivable.validators import validate_ar_separation_of_duties
from apps.customers.models import Customer

logger = logging.getLogger(__name__)


class ReceivableAdjustmentService:
    """Service layer managing receivable adjustments and formal debt write-offs."""

    def __init__(self, number_generator: ARNumberGenerator | None = None) -> None:
        self.number_generator = number_generator or ARNumberGenerator()

    @transaction.atomic
    def create_adjustment(
        self,
        tenant: Any,
        receivable: CustomerReceivable,
        amount: Decimal | float | int,
        adjustment_type: str = ARAdjustmentType.CREDIT_ADJUSTMENT,
        reason: str = "",
        reference: str = "",
        user: Any | None = None,
        approver: Any | None = None,
    ) -> ReceivableAdjustment:
        """Create and post a debit or credit adjustment against a customer receivable."""
        rx = CustomerReceivable.objects.select_for_update().get(pk=receivable.pk, tenant=tenant)
        cust = Customer.objects.select_for_update().get(pk=rx.customer.pk, tenant=tenant)

        adj_amount = Decimal(str(amount))
        if adj_amount <= Decimal("0.0000"):
            raise ValueError("Adjustment amount must be greater than zero.")

        validate_ar_separation_of_duties(user, approver)

        adj_num = self.number_generator.generate_adjustment_number(tenant)

        adjustment = ReceivableAdjustment.objects.create(
            tenant=tenant,
            company=rx.company,
            customer=cust,
            receivable=rx,
            adjustment_number=adj_num,
            adjustment_type=adjustment_type,
            amount=adj_amount,
            reason=reason,
            reference=reference,
            status=ARAdjustmentStatus.APPROVED,
            approved_by=approver or user,
            created_by=user,
        )

        if adjustment_type == ARAdjustmentType.CREDIT_ADJUSTMENT:
            rx.adjusted_amount += adj_amount
            cust.current_balance -= adj_amount
        elif adjustment_type == ARAdjustmentType.DEBIT_ADJUSTMENT:
            rx.adjusted_amount -= adj_amount
            cust.current_balance += adj_amount

        rx.recalculate_balances()
        rx.save(update_fields=["adjusted_amount", "outstanding_amount", "status", "updated_at"])
        cust.save(update_fields=["current_balance", "updated_at"])

        logger.info(f"Created ReceivableAdjustment {adj_num} (${adj_amount}) for receivable {rx.receivable_number}")
        return adjustment

    @transaction.atomic
    def write_off_receivable(
        self,
        tenant: Any,
        receivable: CustomerReceivable,
        amount: Decimal | float | int,
        reason: str,
        approver: Any,
        user: Any | None = None,
    ) -> ReceivableWriteOff:
        """Process a formal uncollectible bad debt write-off against an open receivable."""
        rx = CustomerReceivable.objects.select_for_update().get(pk=receivable.pk, tenant=tenant)
        cust = Customer.objects.select_for_update().get(pk=rx.customer.pk, tenant=tenant)

        write_off_qty = Decimal(str(amount))
        if write_off_qty <= Decimal("0.0000"):
            raise ValueError("Write-off amount must be greater than zero.")

        validate_ar_separation_of_duties(user, approver)

        wof_num = self.number_generator.generate_write_off_number(tenant)

        write_off = ReceivableWriteOff.objects.create(
            tenant=tenant,
            company=rx.company,
            customer=cust,
            receivable=rx,
            write_off_number=wof_num,
            amount=write_off_qty,
            reason=reason,
            approved_by=approver,
            created_by=user,
        )

        rx.adjusted_amount += write_off_qty
        rx.recalculate_balances()
        if rx.outstanding_amount <= Decimal("0.0000"):
            rx.status = ARStatus.WRITTEN_OFF
        rx.save(update_fields=["adjusted_amount", "outstanding_amount", "status", "updated_at"])

        cust.current_balance -= write_off_qty
        cust.save(update_fields=["current_balance", "updated_at"])

        logger.info(f"Processed bad debt write-off {wof_num} (${write_off_qty}) for receivable {rx.receivable_number}")
        return write_off
