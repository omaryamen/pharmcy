"""PrescriptionReviewService managing pharmacist clinical reviews of uploaded order prescriptions."""

from __future__ import annotations

import logging
from typing import Any
from django.utils import timezone

from apps.commerce.models import OrderPrescription, PrescriptionReviewStatus
from apps.notifications.services import EventPublisherService

logger = logging.getLogger(__name__)


class PrescriptionReviewService:
    """Service layer approving or rejecting online order prescription uploads."""

    def __init__(self, event_publisher: EventPublisherService | None = None) -> None:
        self.event_publisher = event_publisher or EventPublisherService()

    def approve_prescription(
        self,
        prescription: OrderPrescription,
        *,
        pharmacist_user: Any,
        notes: str = "",
    ) -> None:
        """Approve prescription document, allowing order fulfillment."""
        prescription.review_status = PrescriptionReviewStatus.APPROVED
        prescription.reviewed_by = pharmacist_user
        prescription.reviewed_at = timezone.now()
        prescription.pharmacist_notes = notes
        prescription.save(update_fields=["review_status", "reviewed_by", "reviewed_at", "pharmacist_notes", "updated_at"])

        self.event_publisher.publish_event(
            tenant=prescription.tenant,
            event_type="prescription.approved",
            source_module="commerce",
            source_object_id=str(prescription.pk),
            payload={"order_number": prescription.order.order_number, "pharmacist": str(pharmacist_user)},
        )
        logger.info("Pharmacist %s approved prescription for Order %s", pharmacist_user, prescription.order.order_number)

    def reject_prescription(
        self,
        prescription: OrderPrescription,
        *,
        pharmacist_user: Any,
        reason: str,
    ) -> None:
        """Reject prescription document with mandatory clinical reason."""
        prescription.review_status = PrescriptionReviewStatus.REJECTED
        prescription.reviewed_by = pharmacist_user
        prescription.reviewed_at = timezone.now()
        prescription.pharmacist_notes = reason
        prescription.save(update_fields=["review_status", "reviewed_by", "reviewed_at", "pharmacist_notes", "updated_at"])

        self.event_publisher.publish_event(
            tenant=prescription.tenant,
            event_type="prescription.rejected",
            source_module="commerce",
            source_object_id=str(prescription.pk),
            payload={"order_number": prescription.order.order_number, "reason": reason},
        )
        logger.warning("Pharmacist %s rejected prescription for Order %s (Reason: %s)", pharmacist_user, prescription.order.order_number, reason)
