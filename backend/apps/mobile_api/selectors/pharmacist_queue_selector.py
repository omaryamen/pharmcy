"""PharmacistMobileSelector retrieving pending clinical review queues and controlled drug orders."""

from __future__ import annotations

from typing import Any
from apps.commerce.models import OrderPrescription, PrescriptionReviewStatus
from apps.core.models import Tenant
from apps.prescriptions.models import Prescription, PrescriptionStatus


class PharmacistMobileSelector:
    """Selector retrieving pharmacist verification queues, pending dispensations, and prescription orders."""

    def get_pharmacist_queue(self, tenant: Tenant) -> dict[str, Any]:
        """Aggregate uploaded online order prescriptions and in-store clinical prescriptions awaiting verification."""
        # 1. E-Commerce Uploaded Prescriptions
        commerce_rx_list = list(
            OrderPrescription.objects.filter(
                tenant=tenant,
                review_status__in=[PrescriptionReviewStatus.UPLOADED, PrescriptionReviewStatus.UNDER_REVIEW],
            )
            .select_related("order", "customer")
            .order_by("created_at")[:20]
            .values(
                "id",
                "order__order_number",
                "customer__first_name",
                "customer__last_name",
                "file_url",
                "review_status",
                "created_at",
            )
        )

        # 2. In-Store Clinical Prescriptions
        pending_prescriptions_count = Prescription.objects.filter(
            tenant=tenant,
            status=PrescriptionStatus.PENDING_VERIFICATION,
        ).count()

        return {
            "pending_ecommerce_prescriptions_count": len(commerce_rx_list),
            "pending_clinical_prescriptions_count": pending_prescriptions_count,
            "ecommerce_prescriptions": commerce_rx_list,
        }
