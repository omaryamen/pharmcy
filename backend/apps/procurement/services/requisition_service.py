"""Authoritative PurchaseRequisition domain service."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.procurement.exceptions import (
    InvalidRequisitionStateError,
    RequisitionAlreadyConvertedError,
)
from apps.procurement.models import (
    ProcurementPriority,
    ProcurementReason,
    PurchaseOrder,
    PurchaseRequisition,
    PurchaseRequisitionLine,
    RequisitionStatus,
)
from apps.procurement.repositories import (
    PurchaseRequisitionLineRepository,
    PurchaseRequisitionRepository,
)
from apps.procurement.services.number_generator import ProcurementNumberGenerator
from apps.procurement.validators import (
    validate_medicine_eligible_for_procurement,
    validate_positive_quantity,
    validate_supplier_eligible_for_procurement,
)

logger = logging.getLogger(__name__)


class PurchaseRequisitionService:
    """Core domain service managing PurchaseRequisition creation, submission, approval, and conversion to PurchaseOrder."""

    def __init__(self):
        self.repository = PurchaseRequisitionRepository()
        self.line_repository = PurchaseRequisitionLineRepository()
        self.number_generator = ProcurementNumberGenerator()

    @transaction.atomic
    def create_requisition(
        self,
        tenant: Any,
        company: Any,
        warehouse: Any,
        lines_data: list[dict[str, Any]],
        *,
        branch: Any | None = None,
        department: str = "",
        priority: str = ProcurementPriority.NORMAL,
        reason: str = ProcurementReason.REGULAR_REPLENISHMENT,
        required_date: Any | None = None,
        notes: str = "",
        user: Any | None = None,
    ) -> PurchaseRequisition:
        """Create a new PurchaseRequisition and line items in DRAFT status."""
        req_num = self.number_generator.generate_requisition_number(tenant)

        requisition = self.repository.create(
            tenant=tenant,
            company=company,
            branch=branch,
            warehouse=warehouse,
            requisition_number=req_num,
            department=department,
            priority=priority,
            reason=reason,
            status=RequisitionStatus.DRAFT,
            required_date=required_date,
            notes=notes,
            requested_by=user,
        )

        total_est = Decimal("0.0000")

        for line_data in lines_data:
            med = line_data["medicine"]
            validate_medicine_eligible_for_procurement(med, tenant)

            qty = validate_positive_quantity(line_data["requested_quantity"])
            est_cost = Decimal(str(line_data.get("estimated_unit_cost", "0.0000")))

            pref_supp = line_data.get("preferred_supplier")
            if pref_supp:
                validate_supplier_eligible_for_procurement(pref_supp, tenant)

            line = self.line_repository.create(
                tenant=tenant,
                requisition=requisition,
                medicine=med,
                preferred_supplier=pref_supp,
                requested_quantity=qty,
                approved_quantity=qty,
                unit=line_data.get("unit", "Pcs"),
                estimated_unit_cost=est_cost,
                required_date=line_data.get("required_date", required_date),
                notes=line_data.get("notes", ""),
            )
            line.recalculate_total_cost()
            line.save(update_fields=["estimated_total_cost"])

            total_est += line.estimated_total_cost

        requisition.total_estimated_cost = total_est
        requisition.save(update_fields=["total_estimated_cost", "updated_at"])

        logger.info("Created purchase requisition %s for tenant %s", req_num, tenant)
        return requisition

    @transaction.atomic
    def submit_requisition(self, tenant: Any, requisition: PurchaseRequisition, user: Any | None = None) -> PurchaseRequisition:
        """Submit a DRAFT requisition for approval."""
        if requisition.status != RequisitionStatus.DRAFT:
            raise InvalidRequisitionStateError(f"Cannot submit requisition in status {requisition.status}.")

        requisition.status = RequisitionStatus.SUBMITTED
        requisition.save(update_fields=["status", "updated_at"])

        logger.info("Submitted purchase requisition %s", requisition.requisition_number)
        return requisition

    @transaction.atomic
    def approve_requisition(self, tenant: Any, requisition: PurchaseRequisition, user: Any | None = None) -> PurchaseRequisition:
        """Approve a submitted requisition."""
        if requisition.status not in [RequisitionStatus.SUBMITTED, RequisitionStatus.UNDER_REVIEW]:
            raise InvalidRequisitionStateError(f"Cannot approve requisition in status {requisition.status}.")

        now = timezone.now()
        requisition.status = RequisitionStatus.APPROVED
        requisition.approved_at = now
        requisition.approved_by = user
        requisition.save(update_fields=["status", "approved_at", "approved_by", "updated_at"])

        logger.info("Approved purchase requisition %s", requisition.requisition_number)
        return requisition

    @transaction.atomic
    def reject_requisition(self, tenant: Any, requisition: PurchaseRequisition, rejection_reason: str = "", user: Any | None = None) -> PurchaseRequisition:
        """Reject a submitted requisition."""
        if requisition.status not in [RequisitionStatus.SUBMITTED, RequisitionStatus.UNDER_REVIEW]:
            raise InvalidRequisitionStateError(f"Cannot reject requisition in status {requisition.status}.")

        now = timezone.now()
        requisition.status = RequisitionStatus.REJECTED
        requisition.rejected_at = now
        requisition.rejected_by = user
        requisition.rejection_reason = rejection_reason
        requisition.save(update_fields=["status", "rejected_at", "rejected_by", "rejection_reason", "updated_at"])

        logger.info("Rejected purchase requisition %s", requisition.requisition_number)
        return requisition
