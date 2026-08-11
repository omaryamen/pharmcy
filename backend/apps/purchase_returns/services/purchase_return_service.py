"""Authoritative PurchaseReturn domain service integrating Stock Movement Engine and Supplier Acceptance."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.inventory.repositories import InventoryItemRepository
from apps.procurement.models import ProcurementPriority
from apps.purchase_returns.exceptions import (
    CannotCancelDispatchedReturnError,
    ExceedsReturnableQuantityError,
    InvalidReturnStateError,
    ReturnAlreadyDispatchedError,
)
from apps.purchase_returns.models import (
    CreditNoteStatus,
    DiscrepancyReason,
    DiscrepancyStatus,
    ProductCondition,
    PurchaseReturn,
    PurchaseReturnLine,
    ReturnDiscrepancy,
    ReturnReason,
    ReturnStatus,
    SupplierCreditNote,
)
from apps.purchase_returns.repositories import (
    PurchaseReturnLineRepository,
    PurchaseReturnRepository,
    ReturnDiscrepancyRepository,
    SupplierCreditNoteRepository,
)
from apps.purchase_returns.services.number_generator import PurchaseReturnNumberGenerator
from apps.purchase_returns.validators import (
    validate_return_approval_separation_of_duties,
    validate_return_eligibility,
)
from apps.stock_movement.models import MovementType, ReferenceType
from apps.stock_movement.services import StockMovementEngine

logger = logging.getLogger(__name__)


class PurchaseReturnService:
    """Core domain service managing PurchaseReturn creation, approvals, picking, dispatching via Stock Movement Engine, supplier acceptance, and credit notes."""

    def __init__(self):
        self.repository = PurchaseReturnRepository()
        self.line_repository = PurchaseReturnLineRepository()
        self.discrepancy_repository = ReturnDiscrepancyRepository()
        self.credit_note_repository = SupplierCreditNoteRepository()
        self.number_generator = PurchaseReturnNumberGenerator()
        self.inventory_item_repository = InventoryItemRepository()
        self.movement_engine = StockMovementEngine()

    @transaction.atomic
    def create_purchase_return(
        self,
        tenant: Any,
        company: Any,
        supplier: Any,
        warehouse: Any,
        lines_data: list[dict[str, Any]],
        *,
        branch: Any | None = None,
        purchase_order: Any | None = None,
        goods_receipt: Any | None = None,
        return_date: Any | None = None,
        return_reason: str = ReturnReason.DAMAGED,
        priority: str = ProcurementPriority.NORMAL,
        currency: str = "USD",
        exchange_rate: Decimal | float | str = "1.000000",
        other_charges: Decimal | float | str = "0.0000",
        notes: str = "",
        idempotency_key: str = "",
        user: Any | None = None,
    ) -> PurchaseReturn:
        """Create a PurchaseReturn header and lines in DRAFT status."""
        if idempotency_key:
            existing = self.repository.find_by_idempotency_key(tenant, idempotency_key)
            if existing:
                logger.info("Found existing PurchaseReturn %s for idempotency_key %s", existing.return_number, idempotency_key)
                return existing

        ret_dt = return_date or timezone.now().date()
        ret_num = self.number_generator.generate_return_number(tenant)

        purchase_return = self.repository.create(
            tenant=tenant,
            company=company,
            branch=branch,
            supplier=supplier,
            purchase_order=purchase_order,
            goods_receipt=goods_receipt,
            warehouse=warehouse,
            return_number=ret_num,
            return_date=ret_dt,
            status=ReturnStatus.DRAFT,
            return_reason=return_reason,
            priority=priority,
            currency=currency,
            exchange_rate=Decimal(str(exchange_rate)),
            other_charges=Decimal(str(other_charges)),
            notes=notes,
            idempotency_key=idempotency_key,
            requested_by=user,
        )

        subtotal = Decimal("0.0000")
        total_discount = Decimal("0.0000")
        total_tax = Decimal("0.0000")

        for line_data in lines_data:
            med = line_data["medicine"]
            batch = line_data["batch"]
            loc = line_data["storage_location"]

            req_qty = Decimal(str(line_data["requested_return_quantity"]))
            app_qty = Decimal(str(line_data.get("approved_return_quantity", str(req_qty))))

            u_cost = Decimal(str(line_data.get("unit_cost", str(batch.unit_cost))))
            disc = Decimal(str(line_data.get("discount", "0.0000")))
            tx = Decimal(str(line_data.get("tax", "0.0000")))

            inv_item = self.inventory_item_repository.get_exact_stock_position(
                tenant=tenant,
                warehouse_id=warehouse.id,
                storage_location_id=loc.id,
                medicine_id=med.id,
                batch_id=batch.id,
            )
            avail_stock = inv_item.available_quantity if inv_item else Decimal("0.00")

            validate_return_eligibility(
                medicine=med,
                batch=batch,
                requested_quantity=req_qty,
                available_stock_quantity=avail_stock,
            )

            line = self.line_repository.create(
                tenant=tenant,
                purchase_return=purchase_return,
                medicine=med,
                batch=batch,
                goods_receipt_line=line_data.get("goods_receipt_line"),
                purchase_order_line=line_data.get("purchase_order_line"),
                storage_location=loc,
                available_quantity=avail_stock,
                requested_return_quantity=req_qty,
                approved_return_quantity=app_qty,
                unit=line_data.get("unit", "Pcs"),
                unit_cost=u_cost,
                discount=disc,
                tax=tx,
                return_reason=line_data.get("return_reason", return_reason),
                condition=line_data.get("condition", ProductCondition.SEALED),
                notes=line_data.get("notes", ""),
            )
            line.calculate_total_value()
            line.save()

            subtotal += (app_qty * u_cost)
            total_discount += disc
            total_tax += tx

        purchase_return.subtotal = subtotal
        purchase_return.discount = total_discount
        purchase_return.tax = total_tax
        purchase_return.grand_total = (subtotal - total_discount) + total_tax + purchase_return.other_charges
        purchase_return.save(update_fields=["subtotal", "discount", "tax", "grand_total", "updated_at"])

        logger.info("Created PurchaseReturn %s for supplier %s", ret_num, supplier.legal_name)
        return purchase_return

    @transaction.atomic
    def request_purchase_return(self, tenant: Any, purchase_return: PurchaseReturn, user: Any | None = None) -> PurchaseReturn:
        """Submit a DRAFT purchase return for manager approval."""
        if purchase_return.status != ReturnStatus.DRAFT:
            raise InvalidReturnStateError(f"Cannot submit purchase return in status {purchase_return.status}.")

        purchase_return.status = ReturnStatus.PENDING_APPROVAL
        purchase_return.save(update_fields=["status", "updated_at"])

        logger.info("Requested PurchaseReturn %s for approval", purchase_return.return_number)
        return purchase_return

    @transaction.atomic
    def approve_purchase_return(self, tenant: Any, purchase_return: PurchaseReturn, user: Any | None = None) -> PurchaseReturn:
        """Approve a pending purchase return, enforcing separation of duties."""
        if purchase_return.status not in [ReturnStatus.PENDING_APPROVAL, ReturnStatus.DRAFT]:
            raise InvalidReturnStateError(f"Cannot approve purchase return in status {purchase_return.status}.")

        validate_return_approval_separation_of_duties(
            purchase_return.requested_by, user, is_superuser=getattr(user, "is_superuser", False)
        )

        now = timezone.now()
        purchase_return.status = ReturnStatus.APPROVED
        purchase_return.approved_at = now
        purchase_return.approved_by = user
        purchase_return.save(update_fields=["status", "approved_at", "approved_by", "updated_at"])

        logger.info("Approved PurchaseReturn %s", purchase_return.return_number)
        return purchase_return

    @transaction.atomic
    def dispatch_purchase_return(self, tenant: Any, purchase_return: PurchaseReturn, user: Any | None = None) -> PurchaseReturn:
        """AUTHORITATIVE DISPATCH ENGINE: Removes returned stock from inventory via StockMovementEngine.

        Guarantees:
        1. Atomic execution inside @transaction.atomic block.
        2. Absolute zero direct inventory balance mutations.
        3. Re-validates current stock balances prior to physical removal.
        4. Idempotent execution (returns cleanly if already DISPATCHED).
        """
        purchase_return = (
            PurchaseReturn.objects.filter(tenant=tenant, pk=purchase_return.pk)
            .select_for_update()
            .first()
        )
        if not purchase_return:
            raise InvalidReturnStateError("Purchase return does not exist.")

        if purchase_return.status in [ReturnStatus.DISPATCHED, ReturnStatus.ACCEPTED, ReturnStatus.CLOSED]:
            logger.info("PurchaseReturn %s is already dispatched. Returning existing object.", purchase_return.return_number)
            return purchase_return

        if purchase_return.status not in [ReturnStatus.APPROVED, ReturnStatus.PICKING, ReturnStatus.READY_FOR_DISPATCH]:
            raise InvalidReturnStateError(f"Cannot dispatch purchase return in status {purchase_return.status}.")

        lines = list(purchase_return.lines.select_related("medicine", "batch", "storage_location"))

        for line in lines:
            inv_item = self.inventory_item_repository.get_exact_stock_position(
                tenant=tenant,
                warehouse_id=purchase_return.warehouse.id,
                storage_location_id=line.storage_location.id,
                medicine_id=line.medicine.id,
                batch_id=line.batch.id,
            )
            avail_stock = inv_item.available_quantity if inv_item else Decimal("0.00")

            if line.approved_return_quantity > avail_stock:
                raise ExceedsReturnableQuantityError(
                    f"Cannot dispatch return line for {line.medicine.english_name}. "
                    f"Dispatch quantity ({line.approved_return_quantity}) exceeds available stock balance ({avail_stock})."
                )

            # PROCESS PHYSICAL STOCK MOVEMENT VIA STOCK MOVEMENT ENGINE
            self.movement_engine.create_movement(
                tenant=tenant,
                company=purchase_return.company,
                branch=purchase_return.branch,
                warehouse=purchase_return.warehouse,
                source_warehouse=purchase_return.warehouse,
                source_location=line.storage_location,
                movement_type=MovementType.PURCHASE_RETURN,
                medicine=line.medicine,
                batch=line.batch,
                quantity=line.approved_return_quantity,
                unit_cost=line.unit_cost,
                reference_type=ReferenceType.PURCHASE_ORDER if purchase_return.purchase_order else ReferenceType.OTHER,
                reference_id=str(purchase_return.pk),
                reference_number=purchase_return.return_number,
                reason=f"Purchase Return Dispatch: {purchase_return.return_number}",
                idempotency_key=f"PRT-DISP-{purchase_return.pk}-{line.pk}",
                performed_by=user,
                auto_process=True,
            )

            line.dispatched_quantity = line.approved_return_quantity
            line.save(update_fields=["dispatched_quantity"])

        now = timezone.now()
        purchase_return.status = ReturnStatus.DISPATCHED
        purchase_return.dispatched_at = now
        purchase_return.dispatched_by = user
        purchase_return.save(update_fields=["status", "dispatched_at", "dispatched_by", "updated_at"])

        logger.info("Successfully dispatched PurchaseReturn %s and removed stock via StockMovementEngine", purchase_return.return_number)
        return purchase_return

    @transaction.atomic
    def record_supplier_acceptance(
        self,
        tenant: Any,
        purchase_return: PurchaseReturn,
        line_acceptances: list[dict[str, Any]],
        *,
        supplier_reference: str = "",
        notes: str = "",
        user: Any | None = None,
    ) -> PurchaseReturn:
        """Record supplier acceptance/rejection results, generating ReturnDiscrepancy and SupplierCreditNote where required."""
        purchase_return = (
            PurchaseReturn.objects.filter(tenant=tenant, pk=purchase_return.pk)
            .select_for_update()
            .first()
        )
        if not purchase_return:
            raise InvalidReturnStateError("Purchase return does not exist.")

        if purchase_return.status not in [ReturnStatus.DISPATCHED, ReturnStatus.IN_TRANSIT, ReturnStatus.PARTIALLY_ACCEPTED]:
            raise InvalidReturnStateError(f"Cannot record supplier acceptance for return in status {purchase_return.status}.")

        total_accepted_val = Decimal("0.0000")
        total_tax_val = Decimal("0.0000")
        has_discrepancy = False

        for item in line_acceptances:
            line_id = item["line_id"]
            acc_qty = Decimal(str(item.get("supplier_accepted_quantity", "0.0000")))
            rej_qty = Decimal(str(item.get("supplier_rejected_quantity", "0.0000")))

            line = PurchaseReturnLine.objects.filter(tenant=tenant, purchase_return=purchase_return, pk=line_id).first()
            if not line:
                continue

            line.supplier_accepted_quantity = acc_qty
            line.supplier_rejected_quantity = rej_qty
            line.save(update_fields=["supplier_accepted_quantity", "supplier_rejected_quantity"])

            total_accepted_val += (acc_qty * line.unit_cost)
            total_tax_val += line.tax

            # Check if discrepancy occurred
            if rej_qty > Decimal("0.0000") or acc_qty < line.dispatched_quantity:
                has_discrepancy = True
                diff = line.dispatched_quantity - acc_qty

                disc_num = self.number_generator.generate_discrepancy_number(tenant)
                self.discrepancy_repository.create(
                    tenant=tenant,
                    purchase_return=purchase_return,
                    return_line=line,
                    discrepancy_number=disc_num,
                    expected_quantity=line.dispatched_quantity,
                    dispatched_quantity=line.dispatched_quantity,
                    supplier_accepted_quantity=acc_qty,
                    supplier_rejected_quantity=rej_qty,
                    difference=diff,
                    reason=item.get("discrepancy_reason", DiscrepancyReason.SHORTAGE),
                    evidence=item.get("evidence", ""),
                    status=DiscrepancyStatus.PENDING,
                    created_by=user,
                )

        # Generate Supplier Credit Note foundation
        if total_accepted_val > Decimal("0.0000"):
            crn_num = self.number_generator.generate_credit_note_number(tenant)
            self.credit_note_repository.create(
                tenant=tenant,
                purchase_return=purchase_return,
                supplier=purchase_return.supplier,
                credit_note_number=crn_num,
                supplier_reference=supplier_reference,
                accepted_value=total_accepted_val,
                tax_value=total_tax_val,
                net_credit_value=total_accepted_val + total_tax_val,
                currency=purchase_return.currency,
                status=CreditNoteStatus.EXPECTED,
                notes=f"Generated from Purchase Return {purchase_return.return_number}",
            )

        now = timezone.now()
        new_status = ReturnStatus.DISCREPANCY if has_discrepancy else ReturnStatus.ACCEPTED
        purchase_return.status = new_status
        purchase_return.completed_at = now
        purchase_return.received_by = user
        purchase_return.save(update_fields=["status", "completed_at", "received_by", "updated_at"])

        logger.info("Recorded supplier acceptance for PurchaseReturn %s (Status: %s)", purchase_return.return_number, new_status)
        return purchase_return

    @transaction.atomic
    def reverse_purchase_return(self, tenant: Any, purchase_return: PurchaseReturn, reason: str = "", user: Any | None = None) -> PurchaseReturn:
        """Reverse a dispatched purchase return, restoring inventory through compensating StockMovementEngine movements."""
        purchase_return = (
            PurchaseReturn.objects.filter(tenant=tenant, pk=purchase_return.pk)
            .select_for_update()
            .first()
        )
        if not purchase_return:
            raise InvalidReturnStateError("Purchase return does not exist.")

        if purchase_return.status not in [ReturnStatus.DISPATCHED, ReturnStatus.ACCEPTED, ReturnStatus.DISCREPANCY]:
            raise InvalidReturnStateError(f"Cannot reverse purchase return in status {purchase_return.status}.")

        # Create compensating receipt movements for dispatched quantities
        for line in purchase_return.lines.all():
            if line.dispatched_quantity > Decimal("0.0000"):
                self.movement_engine.create_movement(
                    tenant=tenant,
                    company=purchase_return.company,
                    branch=purchase_return.branch,
                    warehouse=purchase_return.warehouse,
                    destination_warehouse=purchase_return.warehouse,
                    destination_location=line.storage_location,
                    movement_type=MovementType.RECEIPT,
                    medicine=line.medicine,
                    batch=line.batch,
                    quantity=line.dispatched_quantity,
                    unit_cost=line.unit_cost,
                    reference_type=ReferenceType.OTHER,
                    reference_id=str(purchase_return.pk),
                    reference_number=purchase_return.return_number,
                    reason=f"Purchase Return Reversal: {reason}",
                    idempotency_key=f"PRT-REV-{purchase_return.pk}-{line.pk}",
                    performed_by=user,
                    auto_process=True,
                )

        purchase_return.status = ReturnStatus.REVERSED
        purchase_return.notes = f"{purchase_return.notes}\n[REVERSED]: {reason}".strip()
        purchase_return.save(update_fields=["status", "notes", "updated_at"])

        logger.info("Reversed PurchaseReturn %s", purchase_return.return_number)
        return purchase_return
