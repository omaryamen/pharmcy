"""Authoritative PurchaseOrder domain service."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.procurement.exceptions import (
    CannotCancelReceivedPOError,
    InvalidAmendmentError,
    InvalidPurchaseOrderStateError,
    RequisitionAlreadyConvertedError,
)
from apps.procurement.models import (
    AmendmentStatus,
    ProcurementPriority,
    PurchaseOrder,
    PurchaseOrderAmendment,
    PurchaseOrderLine,
    PurchaseOrderStatus,
    PurchaseRequisition,
    RequisitionStatus,
)
from apps.procurement.repositories import (
    PurchaseOrderAmendmentRepository,
    PurchaseOrderLineRepository,
    PurchaseOrderRepository,
)
from apps.procurement.services.number_generator import ProcurementNumberGenerator
from apps.procurement.validators import (
    validate_medicine_eligible_for_procurement,
    validate_non_negative_amount,
    validate_po_approval_separation_of_duties,
    validate_positive_quantity,
    validate_supplier_eligible_for_procurement,
)

logger = logging.getLogger(__name__)


class PurchaseOrderService:
    """Core domain service managing PurchaseOrder creation, approvals, amendments, cancellations, and requisition conversion."""

    def __init__(self):
        self.repository = PurchaseOrderRepository()
        self.line_repository = PurchaseOrderLineRepository()
        self.amendment_repository = PurchaseOrderAmendmentRepository()
        self.number_generator = ProcurementNumberGenerator()

    @transaction.atomic
    def create_purchase_order(
        self,
        tenant: Any,
        company: Any,
        supplier: Any,
        warehouse: Any,
        lines_data: list[dict[str, Any]],
        *,
        branch: Any | None = None,
        requisition: PurchaseRequisition | None = None,
        supplier_reference: str = "",
        order_date: Any | None = None,
        expected_delivery_date: Any | None = None,
        currency: str = "USD",
        exchange_rate: Decimal | float | str = "1.000000",
        payment_terms: str = "Net 30",
        priority: str = ProcurementPriority.NORMAL,
        shipping_cost: Decimal | float | str = "0.0000",
        other_charges: Decimal | float | str = "0.0000",
        notes: str = "",
        terms_and_conditions: str = "",
        idempotency_key: str = "",
        user: Any | None = None,
    ) -> PurchaseOrder:
        """Create a new PurchaseOrder header and line items in DRAFT status."""
        if idempotency_key:
            existing = self.repository.find_by_idempotency_key(tenant, idempotency_key)
            if existing:
                logger.info("Found existing PO %s for idempotency_key %s", existing.po_number, idempotency_key)
                return existing

        validate_supplier_eligible_for_procurement(supplier, tenant)

        order_dt = order_date or timezone.now().date()
        po_num = self.number_generator.generate_po_number(tenant)

        po = self.repository.create(
            tenant=tenant,
            company=company,
            branch=branch,
            supplier=supplier,
            warehouse=warehouse,
            requisition=requisition,
            po_number=po_num,
            supplier_reference=supplier_reference,
            order_date=order_dt,
            expected_delivery_date=expected_delivery_date,
            currency=currency,
            exchange_rate=Decimal(str(exchange_rate)),
            payment_terms=payment_terms,
            status=PurchaseOrderStatus.DRAFT,
            priority=priority,
            shipping_cost=validate_non_negative_amount(shipping_cost),
            other_charges=validate_non_negative_amount(other_charges),
            notes=notes,
            terms_and_conditions=terms_and_conditions,
            idempotency_key=idempotency_key,
            created_by=user,
        )

        subtotal = Decimal("0.0000")
        total_discount = Decimal("0.0000")
        total_tax = Decimal("0.0000")

        for line_data in lines_data:
            med = line_data["medicine"]
            validate_medicine_eligible_for_procurement(med, tenant)

            qty = validate_positive_quantity(line_data["ordered_quantity"])
            free_qty = validate_non_negative_amount(line_data.get("free_quantity", "0.0000"))
            u_price = validate_non_negative_amount(line_data.get("unit_price", "0.0000"))

            disc_pct = validate_non_negative_amount(line_data.get("discount_percentage", "0.00"))
            tax_pct = validate_non_negative_amount(line_data.get("tax_percentage", "0.00"))

            line = self.line_repository.create(
                tenant=tenant,
                purchase_order=po,
                medicine=med,
                warehouse=line_data.get("warehouse") or warehouse,
                storage_location=line_data.get("storage_location"),
                supplier_product_code=line_data.get("supplier_product_code", ""),
                supplier_barcode=line_data.get("supplier_barcode", ""),
                description=line_data.get("description", ""),
                ordered_quantity=qty,
                free_quantity=free_qty,
                unit=line_data.get("unit", "Pcs"),
                unit_price=u_price,
                discount_percentage=disc_pct,
                tax_percentage=tax_pct,
                expected_date=line_data.get("expected_date", expected_delivery_date),
                notes=line_data.get("notes", ""),
            )
            line.calculate_totals()
            line.save()

            subtotal += line.line_subtotal
            total_discount += line.discount_amount
            total_tax += line.tax_amount

        po.subtotal = subtotal
        po.discount_amount = total_discount
        po.tax_amount = total_tax
        po.grand_total = (subtotal - total_discount) + total_tax + po.shipping_cost + po.other_charges
        po.save(update_fields=["subtotal", "discount_amount", "tax_amount", "grand_total", "updated_at"])

        logger.info("Created Purchase Order %s for supplier %s", po_num, supplier.legal_name)
        return po

    @transaction.atomic
    def submit_purchase_order(self, tenant: Any, po: PurchaseOrder, user: Any | None = None) -> PurchaseOrder:
        """Submit a DRAFT Purchase Order for approval."""
        if po.status != PurchaseOrderStatus.DRAFT:
            raise InvalidPurchaseOrderStateError(f"Cannot submit Purchase Order in status {po.status}.")

        po.status = PurchaseOrderStatus.PENDING_APPROVAL
        po.save(update_fields=["status", "updated_at"])

        logger.info("Submitted Purchase Order %s for approval", po.po_number)
        return po

    @transaction.atomic
    def approve_purchase_order(self, tenant: Any, po: PurchaseOrder, user: Any | None = None) -> PurchaseOrder:
        """Approve a Purchase Order, enforcing separation of duties."""
        if po.status not in [PurchaseOrderStatus.PENDING_APPROVAL, PurchaseOrderStatus.DRAFT]:
            raise InvalidPurchaseOrderStateError(f"Cannot approve Purchase Order in status {po.status}.")

        validate_po_approval_separation_of_duties(
            po.created_by, user, is_superuser=getattr(user, "is_superuser", False)
        )

        now = timezone.now()
        po.status = PurchaseOrderStatus.APPROVED
        po.approved_at = now
        po.approved_by = user
        po.save(update_fields=["status", "approved_at", "approved_by", "updated_at"])

        logger.info("Approved Purchase Order %s", po.po_number)
        return po

    @transaction.atomic
    def reject_purchase_order(self, tenant: Any, po: PurchaseOrder, user: Any | None = None) -> PurchaseOrder:
        """Reject a pending Purchase Order."""
        if po.status not in [PurchaseOrderStatus.PENDING_APPROVAL, PurchaseOrderStatus.DRAFT]:
            raise InvalidPurchaseOrderStateError(f"Cannot reject Purchase Order in status {po.status}.")

        po.status = PurchaseOrderStatus.REJECTED
        po.save(update_fields=["status", "updated_at"])

        logger.info("Rejected Purchase Order %s", po.po_number)
        return po

    @transaction.atomic
    def send_to_supplier(self, tenant: Any, po: PurchaseOrder, user: Any | None = None) -> PurchaseOrder:
        """Mark Purchase Order as sent to supplier."""
        if po.status not in [PurchaseOrderStatus.APPROVED, PurchaseOrderStatus.SENT_TO_SUPPLIER]:
            raise InvalidPurchaseOrderStateError(f"Cannot send Purchase Order in status {po.status}.")

        now = timezone.now()
        po.status = PurchaseOrderStatus.SENT_TO_SUPPLIER
        po.sent_at = now
        po.save(update_fields=["status", "sent_at", "updated_at"])

        logger.info("Sent Purchase Order %s to supplier", po.po_number)
        return po

    @transaction.atomic
    def acknowledge_order(self, tenant: Any, po: PurchaseOrder, user: Any | None = None) -> PurchaseOrder:
        """Record supplier acknowledgment of Purchase Order."""
        if po.status not in [PurchaseOrderStatus.SENT_TO_SUPPLIER, PurchaseOrderStatus.ACKNOWLEDGED]:
            raise InvalidPurchaseOrderStateError(f"Cannot acknowledge Purchase Order in status {po.status}.")

        now = timezone.now()
        po.status = PurchaseOrderStatus.ACKNOWLEDGED
        po.acknowledged_at = now
        po.save(update_fields=["status", "acknowledged_at", "updated_at"])

        logger.info("Acknowledged Purchase Order %s", po.po_number)
        return po

    @transaction.atomic
    def cancel_purchase_order(self, tenant: Any, po: PurchaseOrder, reason: str, user: Any | None = None) -> PurchaseOrder:
        """Cancel a Purchase Order if receiving has not started."""
        po = (
            PurchaseOrder.objects.filter(tenant=tenant, pk=po.pk)
            .select_for_update()
            .first()
        )
        if not po:
            raise InvalidPurchaseOrderStateError("Purchase Order does not exist.")

        if po.status in [PurchaseOrderStatus.PARTIALLY_RECEIVED, PurchaseOrderStatus.FULLY_RECEIVED, PurchaseOrderStatus.CLOSED]:
            raise CannotCancelReceivedPOError()

        now = timezone.now()
        po.status = PurchaseOrderStatus.CANCELLED
        po.cancelled_at = now
        po.cancelled_by = user
        po.cancellation_reason = reason
        po.save(update_fields=["status", "cancelled_at", "cancelled_by", "cancellation_reason", "updated_at"])

        logger.info("Cancelled Purchase Order %s", po.po_number)
        return po

    @transaction.atomic
    def amend_purchase_order(
        self,
        tenant: Any,
        po: PurchaseOrder,
        reason: str,
        changes: dict[str, Any],
        user: Any | None = None,
    ) -> PurchaseOrderAmendment:
        """Create a controlled PO amendment record and update PO header fields safely."""
        po = (
            PurchaseOrder.objects.filter(tenant=tenant, pk=po.pk)
            .select_for_update()
            .first()
        )
        if not po:
            raise InvalidPurchaseOrderStateError("Purchase Order does not exist.")

        # If receiving has started, block critical field changes
        if po.status in [PurchaseOrderStatus.PARTIALLY_RECEIVED, PurchaseOrderStatus.FULLY_RECEIVED]:
            restricted_fields = ["supplier", "warehouse", "currency"]
            for rf in restricted_fields:
                if rf in changes:
                    raise InvalidAmendmentError(f"Cannot amend critical field '{rf}' once receiving has started.")

        amd_num = self.number_generator.generate_amendment_number(tenant)
        changed_fields_summary = {}

        for field, new_val in changes.items():
            if hasattr(po, field):
                old_val = getattr(po, field)
                changed_fields_summary[field] = {"old": str(old_val), "new": str(new_val)}
                setattr(po, field, new_val)

        po.save()

        now = timezone.now()
        amendment = self.amendment_repository.create(
            tenant=tenant,
            purchase_order=po,
            amendment_number=amd_num,
            reason=reason,
            changed_fields=changed_fields_summary,
            status=AmendmentStatus.APPROVED,
            changed_by=user,
            approved_by=user,
            approved_at=now,
        )

        logger.info("Amended Purchase Order %s with amendment %s", po.po_number, amd_num)
        return amendment

    @transaction.atomic
    def close_purchase_order(self, tenant: Any, po: PurchaseOrder, user: Any | None = None) -> PurchaseOrder:
        """Close an open or partially received Purchase Order."""
        if po.status in [PurchaseOrderStatus.CLOSED, PurchaseOrderStatus.CANCELLED]:
            return po

        po.status = PurchaseOrderStatus.CLOSED
        po.save(update_fields=["status", "updated_at"])

        logger.info("Closed Purchase Order %s", po.po_number)
        return po

    @transaction.atomic
    def convert_requisition_to_purchase_order(
        self,
        tenant: Any,
        requisition: PurchaseRequisition,
        user: Any | None = None,
    ) -> list[PurchaseOrder]:
        """Convert an approved PurchaseRequisition into PurchaseOrder(s) grouped by preferred supplier.

        Guarantees idempotency via select_for_update() row locking to prevent duplicate conversion.
        """
        requisition = (
            PurchaseRequisition.objects.filter(tenant=tenant, pk=requisition.pk)
            .select_for_update()
            .first()
        )
        if not requisition:
            raise InvalidRequisitionStateError("Requisition does not exist.")

        if requisition.status == RequisitionStatus.CONVERTED_TO_PO:
            logger.info("Requisition %s is already converted. Returning existing POs.", requisition.requisition_number)
            return list(requisition.purchase_orders.all())

        if requisition.status != RequisitionStatus.APPROVED:
            raise InvalidRequisitionStateError(f"Cannot convert requisition in status {requisition.status}.")

        lines = list(requisition.lines.select_related("medicine", "preferred_supplier"))

        # Group lines by supplier
        supplier_groups: dict[Any, list[PurchaseRequisitionLine]] = {}
        for line in lines:
            supp = line.preferred_supplier
            if not supp:
                # If no supplier specified, search active supplier or fallback
                from apps.suppliers.models import Supplier
                supp = Supplier.objects.filter(tenant=tenant, status="active").first()
                if not supp:
                    raise InvalidPurchaseOrderStateError("No active supplier found to convert requisition.")

            supplier_groups.setdefault(supp, []).append(line)

        created_pos = []

        for supp, group_lines in supplier_groups.items():
            po_lines_data = []
            for req_line in group_lines:
                po_lines_data.append({
                    "medicine": req_line.medicine,
                    "ordered_quantity": req_line.approved_quantity or req_line.requested_quantity,
                    "unit_price": req_line.estimated_unit_cost,
                    "unit": req_line.unit,
                    "notes": req_line.notes,
                })

            po = self.create_purchase_order(
                tenant=tenant,
                company=requisition.company,
                supplier=supp,
                warehouse=requisition.warehouse,
                lines_data=po_lines_data,
                branch=requisition.branch,
                requisition=requisition,
                priority=requisition.priority,
                notes=f"Converted from Requisition {requisition.requisition_number}",
                user=user,
            )
            created_pos.append(po)

        requisition.status = RequisitionStatus.CONVERTED_TO_PO
        requisition.save(update_fields=["status", "updated_at"])

        logger.info("Converted requisition %s to %d Purchase Order(s)", requisition.requisition_number, len(created_pos))
        return created_pos
