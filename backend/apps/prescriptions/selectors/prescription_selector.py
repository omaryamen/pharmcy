"""Query selector layer for Prescriptions & Dispensing reporting."""

from __future__ import annotations

from typing import Any

from django.db.models import Count, Q, QuerySet

from apps.prescriptions.models import (
    Prescription,
    PrescriptionDispense,
    PrescriptionStatus,
    PrescriptionType,
)


class PrescriptionSelector:
    """Selector providing search, filtering, and reporting analytics for prescriptions and pharmacy dispensing."""

    def list_prescriptions(
        self,
        tenant: Any,
        *,
        company_id: str | None = None,
        branch_id: str | None = None,
        customer_id: str | None = None,
        status: str | None = None,
        rx_type: str | None = None,
        doctor_name: str | None = None,
        search: str | None = None,
    ) -> QuerySet[Prescription]:
        qs = (
            Prescription.objects.filter(tenant=tenant)
            .select_related("company", "branch", "customer", "verified_by", "dispensed_by")
            .prefetch_related("lines__medicine", "lines__substituted_medicine", "dispensations")
        )

        if company_id:
            qs = qs.filter(company_id=company_id)
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        if status:
            qs = qs.filter(status=status)
        if rx_type:
            qs = qs.filter(rx_type=rx_type)
        if doctor_name:
            qs = qs.filter(doctor_name__icontains=doctor_name)
        if search:
            qs = qs.filter(
                Q(rx_number__icontains=search)
                | Q(customer__english_name__icontains=search)
                | Q(customer__first_name__icontains=search)
                | Q(doctor_name__icontains=search)
                | Q(diagnosis_code__icontains=search)
            )

        return qs

    def list_dispensations(
        self,
        tenant: Any,
        *,
        prescription_id: str | None = None,
        customer_id: str | None = None,
        status: str | None = None,
    ) -> QuerySet[PrescriptionDispense]:
        qs = PrescriptionDispense.objects.filter(tenant=tenant).select_related("company", "branch", "warehouse", "prescription", "sales_invoice", "dispensed_by").prefetch_related("lines__medicine", "lines__batch")
        if prescription_id:
            qs = qs.filter(prescription_id=prescription_id)
        if customer_id:
            qs = qs.filter(prescription__customer_id=customer_id)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_dispensing_statistics(
        self,
        tenant: Any,
        *,
        company_id: str | None = None,
        branch_id: str | None = None,
    ) -> dict[str, Any]:
        """Calculate clinical dispensing statistics and controlled substance logs."""
        qs = Prescription.objects.filter(tenant=tenant)
        if company_id:
            qs = qs.filter(company_id=company_id)
        if branch_id:
            qs = qs.filter(branch_id=branch_id)

        total_rx = qs.count()
        pending_verification = qs.filter(status=PrescriptionStatus.PENDING_VERIFICATION).count()
        verified = qs.filter(status=PrescriptionStatus.VERIFIED).count()
        dispensed = qs.filter(status__in=[PrescriptionStatus.PARTIALLY_DISPENSED, PrescriptionStatus.FULLY_DISPENSED]).count()

        controlled_count = qs.filter(
            rx_type__in=[
                PrescriptionType.CONTROLLED_CLASS_A,
                PrescriptionType.CONTROLLED_CLASS_B,
                PrescriptionType.NARCOTIC,
            ]
        ).count()

        return {
            "total_prescriptions": total_rx,
            "pending_verification_count": pending_verification,
            "verified_count": verified,
            "dispensed_count": dispensed,
            "controlled_substances_count": controlled_count,
        }
