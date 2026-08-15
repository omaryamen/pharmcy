"""CommercePaymentService managing payment capture, order settlement, and refunds."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any
from django.db import transaction

from apps.commerce.exceptions import CommerceException
from apps.commerce.models import (
    CommerceOrder,
    CommerceOrderStatus,
    CommercePayment,
    CommercePaymentStatus,
    CommerceRefund,
)
from apps.commerce.services.number_generator import CommerceNumberGenerator
from apps.notifications.services import EventPublisherService

logger = logging.getLogger(__name__)


class CommercePaymentService:
    """Service layer capturing customer payments and processing order refunds."""

    def __init__(self, event_publisher: EventPublisherService | None = None) -> None:
        self.event_publisher = event_publisher or EventPublisherService()

    @transaction.atomic
    def process_payment(
        self,
        order: CommerceOrder,
        amount: Decimal,
        payment_method: str = "card",
        *,
        external_tx_id: str = "",
    ) -> CommercePayment:
        """Capture payment against a commerce order and advance payment/order statuses."""
        payment_number = CommerceNumberGenerator.generate_payment_number()
        payment = CommercePayment.objects.create(
            tenant=order.tenant,
            order=order,
            payment_number=payment_number,
            amount=amount,
            currency=order.currency,
            payment_method=payment_method,
            status=CommercePaymentStatus.PAID,
            external_tx_id=external_tx_id,
        )

        order.payment_status = CommercePaymentStatus.PAID
        if order.status in [CommerceOrderStatus.PENDING, CommerceOrderStatus.PAYMENT_PENDING]:
            order.status = CommerceOrderStatus.CONFIRMED
        order.save(update_fields=["payment_status", "status", "updated_at"])

        self.event_publisher.publish_event(
            tenant=order.tenant,
            event_type="payment.success",
            source_module="commerce",
            source_object_id=str(payment.pk),
            payload={
                "order_number": order.order_number,
                "payment_number": payment.payment_number,
                "amount": float(payment.amount),
            },
        )
        logger.info("Captured payment %s for Order %s (%s %s)", payment.payment_number, order.order_number, amount, order.currency)
        return payment

    @transaction.atomic
    def refund_payment(
        self,
        payment: CommercePayment,
        refund_amount: Decimal,
        reason: str = "Customer Return / Refund",
    ) -> CommerceRefund:
        """Process partial or full refund on a completed payment transaction."""
        if refund_amount > payment.amount:
            raise CommerceException("Refund amount cannot exceed original payment amount.")

        refund_number = CommerceNumberGenerator.generate_refund_number()
        refund = CommerceRefund.objects.create(
            tenant=payment.tenant,
            payment=payment,
            refund_number=refund_number,
            amount=refund_amount,
            currency=payment.currency,
            reason=reason,
        )

        if refund_amount == payment.amount:
            payment.status = CommercePaymentStatus.REFUNDED
            payment.order.payment_status = CommercePaymentStatus.REFUNDED
            payment.order.status = CommerceOrderStatus.REFUNDED
        else:
            payment.status = CommercePaymentStatus.PARTIALLY_REFUNDED
            payment.order.payment_status = CommercePaymentStatus.PARTIALLY_REFUNDED

        payment.save(update_fields=["status", "updated_at"])
        payment.order.save(update_fields=["payment_status", "status", "updated_at"])

        self.event_publisher.publish_event(
            tenant=payment.tenant,
            event_type="refund.created",
            source_module="commerce",
            source_object_id=str(refund.pk),
            payload={
                "refund_number": refund.refund_number,
                "order_number": payment.order.order_number,
                "amount": float(refund.amount),
            },
        )
        logger.info("Issued Refund %s on Payment %s (%s %s)", refund.refund_number, payment.payment_number, refund_amount, payment.currency)
        return refund
