"""SaaSPaymentService handling invoice settlement, GL revenue journal posting, payment refunds, and dunning logs."""

from __future__ import annotations

import logging
import uuid
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.general_ledger.services import JournalPostingService
from apps.notifications.services import EventPublisherService
from apps.saas.exceptions import PaymentProcessingError
from apps.saas.models import (
    PaymentFailureLog,
    PaymentMethod,
    SaaSInvoice,
    SaaSInvoiceStatus,
    SaaSPayment,
    SaaSPaymentRefund,
    SaaSPaymentStatus,
    SaaSSubscriptionStatus,
)
from apps.saas.services.number_generator import SaaSNumberGenerator

logger = logging.getLogger(__name__)


class SaaSPaymentService:
    """Service layer managing SaaS invoice payment settlement, refunds, GL posting, and dunning logs."""

    def __init__(
        self,
        number_generator: SaaSNumberGenerator | None = None,
        journal_service: JournalPostingService | None = None,
        event_publisher: EventPublisherService | None = None,
    ) -> None:
        self.number_generator = number_generator or SaaSNumberGenerator()
        self.journal_service = journal_service or JournalPostingService()
        self.event_publisher = event_publisher or EventPublisherService()

    @transaction.atomic
    def process_invoice_payment(
        self,
        invoice: SaaSInvoice,
        *,
        payment_method: PaymentMethod | None = None,
        provider_name: str = "mock",
        simulate_failure: bool = False,
        actor: Any | None = None,
    ) -> SaaSPayment:
        """Process payment settlement for a SaaSInvoice and post GL journal entries upon success."""
        pay_num = self.number_generator.generate_payment_number(invoice.tenant)

        if simulate_failure:
            payment = SaaSPayment.objects.create(
                tenant=invoice.tenant,
                payment_number=pay_num,
                invoice=invoice,
                amount=invoice.total_amount,
                currency=invoice.currency,
                status=SaaSPaymentStatus.FAILED,
                provider_name=provider_name,
                error_code="CARD_DECLINED",
                error_message="Card declined by issuing bank (Simulated)",
            )

            # Log Dunning Failure
            if invoice.subscription:
                invoice.subscription.status = SaaSSubscriptionStatus.PAST_DUE
                invoice.subscription.save(update_fields=["status", "updated_at"])
                PaymentFailureLog.objects.create(
                    tenant=invoice.tenant,
                    subscription=invoice.subscription,
                    attempt_number=1,
                    error_code="CARD_DECLINED",
                    error_message="Card declined",
                )

            self.event_publisher.publish_event(
                tenant=invoice.tenant,
                event_type="payment.failed",
                source_module="saas",
                source_object_id=payment.payment_number,
                payload={"invoice": invoice.invoice_number, "error": "CARD_DECLINED"},
                actor=actor,
            )
            return payment

        # Successful Payment Processing
        ext_tx_id = f"tx_mock_{uuid.uuid4().hex[:12]}"
        payment = SaaSPayment.objects.create(
            tenant=invoice.tenant,
            payment_number=pay_num,
            invoice=invoice,
            amount=invoice.total_amount,
            currency=invoice.currency,
            status=SaaSPaymentStatus.SUCCEEDED,
            provider_name=provider_name,
            external_transaction_id=ext_tx_id,
        )

        invoice.status = SaaSInvoiceStatus.PAID
        invoice.paid_at = timezone.now()
        invoice.save(update_fields=["status", "paid_at", "updated_at"])

        if invoice.subscription:
            invoice.subscription.status = SaaSSubscriptionStatus.ACTIVE
            invoice.subscription.save(update_fields=["status", "updated_at"])

        # Post Double-Entry General Ledger Journal Entry (Debit Bank 1200, Credit Subscription Revenue 4000)
        try:
            self.journal_service.post_journal_entry(
                tenant=invoice.tenant,
                source_module="saas",
                source_object_id=payment.payment_number,
                entry_date=timezone.now().date(),
                description=f"SaaS Subscription Revenue for Invoice {invoice.invoice_number}",
                lines=[
                    {"account_code": "1200", "debit": invoice.total_amount, "credit": Decimal("0.0000"), "memo": "Bank Settlement"},
                    {"account_code": "4000", "debit": Decimal("0.0000"), "credit": invoice.total_amount, "memo": "SaaS Subscription Revenue"},
                ],
                actor=actor,
            )
        except Exception as e:
            logger.warning("GL Posting skipped/failed for SaaS payment %s: %s", pay_num, str(e))

        self.event_publisher.publish_event(
            tenant=invoice.tenant,
            event_type="payment.succeeded",
            source_module="saas",
            source_object_id=payment.payment_number,
            payload={"invoice": invoice.invoice_number, "amount": str(invoice.total_amount), "currency": invoice.currency},
            actor=actor,
        )

        logger.info("Successfully settled SaaS Invoice %s with Payment %s", invoice.invoice_number, pay_num)
        return payment

    @transaction.atomic
    def process_refund(
        self,
        payment: SaaSPayment,
        refund_amount: Decimal,
        *,
        reason: str = "",
        actor: Any | None = None,
    ) -> SaaSPaymentRefund:
        """Process partial or full refund for a SaaSPayment."""
        if refund_amount > payment.amount:
            raise PaymentProcessingError("Refund amount cannot exceed original payment amount.")

        ref_num = self.number_generator.generate_refund_number(payment.tenant)
        refund = SaaSPaymentRefund.objects.create(
            tenant=payment.tenant,
            refund_number=ref_num,
            payment=payment,
            amount=refund_amount,
            currency=payment.currency,
            reason=reason,
            external_refund_id=f"re_mock_{uuid.uuid4().hex[:10]}",
        )

        payment.status = SaaSPaymentStatus.REFUNDED
        payment.save(update_fields=["status", "updated_at"])

        if payment.invoice:
            payment.invoice.status = SaaSInvoiceStatus.REFUNDED
            payment.invoice.save(update_fields=["status", "updated_at"])

        self.event_publisher.publish_event(
            tenant=payment.tenant,
            event_type="payment.refunded",
            source_module="saas",
            source_object_id=ref_num,
            payload={"payment": payment.payment_number, "amount": str(refund_amount)},
            actor=actor,
        )

        logger.info("Processed Refund %s for Payment %s", ref_num, payment.payment_number)
        return refund
