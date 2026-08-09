"""Authoritative Enterprise Stock Movement Engine service."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.inventory.models.enums import AdjustmentReason, BatchStatus, TransactionType
from apps.inventory.selectors.batch import BatchSelector
from apps.inventory.services import InventoryService
from apps.stock_movement.exceptions import (
    CannotReverseUnprocessedMovementError,
    DuplicateIdempotencyKeyError,
    InvalidMovementStateError,
    MovementAlreadyCancelledError,
    MovementAlreadyProcessedError,
    MovementAlreadyReversedError,
    StockMovementValidationError,
)
from apps.stock_movement.models import MovementStatus, MovementType, ReferenceType, StockMovement, StockMovementLine
from apps.stock_movement.repositories import StockMovementLineRepository, StockMovementRepository
from apps.stock_movement.services.movement_number_generator import MovementNumberGenerator
from apps.stock_movement.validators import (
    validate_batch_eligibility_for_outgoing_movement,
    validate_location_belongs_to_warehouse,
    validate_positive_quantity,
)

logger = logging.getLogger(__name__)


class StockMovementEngine:
    """Central authoritative transaction engine executing double-entry inventory stock movements."""

    def __init__(self):
        self.repository = StockMovementRepository()
        self.line_repository = StockMovementLineRepository()
        self.number_generator = MovementNumberGenerator()
        self.inventory_service = InventoryService()
        self.batch_selector = BatchSelector()

    @transaction.atomic
    def create_movement(
        self,
        tenant: Any,
        company: Any,
        warehouse: Any,
        movement_type: str,
        *,
        branch: Any | None = None,
        source_warehouse: Any | None = None,
        destination_warehouse: Any | None = None,
        source_location: Any | None = None,
        destination_location: Any | None = None,
        medicine: Any | None = None,
        batch: Any | None = None,
        quantity: Decimal | float | int = Decimal("0.00"),
        unit_cost: Decimal | float | int = Decimal("0.0000"),
        reference_type: str = "",
        reference_id: str = "",
        reference_number: str = "",
        reason: str = "",
        notes: str = "",
        idempotency_key: str = "",
        performed_by: Any | None = None,
        approved_by: Any | None = None,
        lines: list[dict[str, Any]] | None = None,
        auto_process: bool = False,
    ) -> StockMovement:
        """Create a stock movement document. If auto_process=True, immediately process physical stock changes."""
        # 1. Idempotency Check
        if idempotency_key:
            existing = self.repository.find_by_idempotency_key(tenant, idempotency_key)
            if existing:
                logger.info("Found existing movement %s for idempotency_key %s", existing.movement_number, idempotency_key)
                return existing

        # 2. Hierarchy Validations
        validate_location_belongs_to_warehouse(source_location, source_warehouse or warehouse)
        validate_location_belongs_to_warehouse(destination_location, destination_warehouse or warehouse)

        movement_num = self.number_generator.generate_number(tenant, movement_type)

        qty_dec = Decimal(str(quantity))
        u_cost_dec = Decimal(str(unit_cost))
        t_cost_dec = qty_dec * u_cost_dec

        movement = self.repository.create(
            tenant=tenant,
            company=company,
            branch=branch,
            warehouse=warehouse,
            source_warehouse=source_warehouse,
            destination_warehouse=destination_warehouse,
            source_location=source_location,
            destination_location=destination_location,
            medicine=medicine,
            batch=batch,
            movement_number=movement_num,
            movement_type=movement_type,
            movement_status=MovementStatus.DRAFT,
            quantity=qty_dec,
            unit_cost=u_cost_dec,
            total_cost=t_cost_dec,
            reference_type=reference_type,
            reference_id=reference_id,
            reference_number=reference_number,
            reason=reason,
            notes=notes,
            idempotency_key=idempotency_key,
            performed_by=performed_by,
            approved_by=approved_by,
        )

        # Build lines if provided
        if lines:
            total_line_qty = Decimal("0.00")
            total_line_cost = Decimal("0.0000")
            for line_data in lines:
                l_qty = validate_positive_quantity(line_data["quantity"])
                l_ucost = Decimal(str(line_data.get("unit_cost", u_cost_dec)))
                l_tcost = l_qty * l_ucost

                validate_location_belongs_to_warehouse(line_data.get("source_location"), source_warehouse or warehouse)
                validate_location_belongs_to_warehouse(line_data.get("destination_location"), destination_warehouse or warehouse)

                self.line_repository.create(
                    tenant=tenant,
                    movement=movement,
                    medicine=line_data["medicine"],
                    batch=line_data.get("batch"),
                    source_location=line_data.get("source_location", source_location),
                    destination_location=line_data.get("destination_location", destination_location),
                    quantity=l_qty,
                    unit=line_data.get("unit", "Pcs"),
                    unit_cost=l_ucost,
                    total_cost=l_tcost,
                    reason=line_data.get("reason", reason),
                    notes=line_data.get("notes", ""),
                )
                total_line_qty += l_qty
                total_line_cost += l_tcost

            movement.quantity = total_line_qty
            movement.total_cost = total_line_cost
            movement.save(update_fields=["quantity", "total_cost"])

        elif medicine:
            # Single item movement header line
            l_qty = validate_positive_quantity(qty_dec)
            self.line_repository.create(
                tenant=tenant,
                movement=movement,
                medicine=medicine,
                batch=batch,
                source_location=source_location,
                destination_location=destination_location,
                quantity=l_qty,
                unit=movement.unit_of_measure,
                unit_cost=u_cost_dec,
                total_cost=t_cost_dec,
                reason=reason,
                notes=notes,
            )

        if auto_process:
            movement = self.process_movement(tenant, movement, performed_by=performed_by)

        return movement

    @transaction.atomic
    def process_movement(self, tenant: Any, movement: StockMovement, performed_by: Any | None = None) -> StockMovement:
        """Execute physical stock position mutations for a StockMovement inside an atomic transaction block."""
        movement = (
            StockMovement.objects.filter(tenant=tenant, pk=movement.pk)
            .select_for_update()
            .first()
        )
        if not movement:
            raise InvalidMovementStateError("Stock movement does not exist.")

        if movement.movement_status == MovementStatus.COMPLETED:
            return movement
        if movement.movement_status == MovementStatus.CANCELLED:
            raise MovementAlreadyCancelledError("Cannot process a cancelled stock movement.")
        if movement.movement_status == MovementStatus.REVERSED:
            raise MovementAlreadyReversedError("Cannot process an already reversed stock movement.")

        lines = list(movement.lines.all())
        if not lines:
            raise StockMovementValidationError("Stock movement has no lines to process.")

        m_type = movement.movement_type
        user = performed_by or movement.performed_by

        for line in lines:
            med = line.medicine
            batch = line.batch
            qty = line.quantity
            unit_cost = line.unit_cost
            src_loc = line.source_location or movement.source_location
            dst_loc = line.destination_location or movement.destination_location

            # Direct stock receipt / opening balance / adjustment increase
            if m_type in [MovementType.RECEIPT, MovementType.OPENING_BALANCE, MovementType.ADJUSTMENT_IN, MovementType.SALE_RETURN, MovementType.CORRECTION]:
                wh = movement.destination_warehouse or movement.warehouse
                target_loc = dst_loc or movement.destination_location
                if not target_loc:
                    raise StockMovementValidationError(f"Destination storage location is required for {m_type}.")

                inv_item = self.inventory_service.get_or_create_inventory_item(
                    tenant=tenant,
                    company=movement.company,
                    warehouse=wh,
                    storage_location=target_loc,
                    medicine=med,
                    batch=batch,
                    unit_cost=unit_cost,
                )
                self.inventory_service.adjust_quantity(
                    tenant=tenant,
                    inventory_item_id=str(inv_item.pk),
                    quantity_delta=qty,
                    transaction_type=TransactionType.RECEIPT if m_type == MovementType.RECEIPT else TransactionType.ADJUSTMENT,
                    unit_cost=unit_cost,
                    reference_number=movement.movement_number,
                    reason=line.reason or movement.reason,
                    performed_by=user,
                )

            # Outgoing stock issue / sale / adjustment decrease / damage / expiry / purchase return
            elif m_type in [MovementType.ISSUE, MovementType.SALE, MovementType.ADJUSTMENT_OUT, MovementType.DAMAGE, MovementType.EXPIRY, MovementType.PURCHASE_RETURN]:
                wh = movement.source_warehouse or movement.warehouse
                target_loc = src_loc or movement.source_location
                if not target_loc:
                    raise StockMovementValidationError(f"Source storage location is required for {m_type}.")

                validate_batch_eligibility_for_outgoing_movement(batch)

                inv_item = self.inventory_service.get_or_create_inventory_item(
                    tenant=tenant,
                    company=movement.company,
                    warehouse=wh,
                    storage_location=target_loc,
                    medicine=med,
                    batch=batch,
                )
                self.inventory_service.adjust_quantity(
                    tenant=tenant,
                    inventory_item_id=str(inv_item.pk),
                    quantity_delta=-qty,
                    transaction_type=TransactionType.ISSUE if m_type in [MovementType.ISSUE, MovementType.SALE] else TransactionType.ADJUSTMENT,
                    unit_cost=unit_cost,
                    reference_number=movement.movement_number,
                    reason=line.reason or movement.reason,
                    performed_by=user,
                )

            # Double-Entry Transfer (Source decreases, Destination increases in same transaction)
            elif m_type in [MovementType.TRANSFER_OUT, MovementType.TRANSFER_IN]:
                src_wh = movement.source_warehouse or movement.warehouse
                dst_wh = movement.destination_warehouse or movement.warehouse

                if not src_loc or not dst_loc:
                    raise StockMovementValidationError("Source and destination storage locations are required for transfers.")

                validate_batch_eligibility_for_outgoing_movement(batch)

                # 1. Deduct from Source
                src_item = self.inventory_service.get_or_create_inventory_item(
                    tenant=tenant,
                    company=movement.company,
                    warehouse=src_wh,
                    storage_location=src_loc,
                    medicine=med,
                    batch=batch,
                )
                self.inventory_service.adjust_quantity(
                    tenant=tenant,
                    inventory_item_id=str(src_item.pk),
                    quantity_delta=-qty,
                    transaction_type=TransactionType.TRANSFER_OUT,
                    unit_cost=unit_cost,
                    reference_number=movement.movement_number,
                    reason=line.reason or movement.reason,
                    performed_by=user,
                )

                # 2. Add to Destination
                dst_item = self.inventory_service.get_or_create_inventory_item(
                    tenant=tenant,
                    company=movement.company,
                    warehouse=dst_wh,
                    storage_location=dst_loc,
                    medicine=med,
                    batch=batch,
                    unit_cost=unit_cost,
                )
                self.inventory_service.adjust_quantity(
                    tenant=tenant,
                    inventory_item_id=str(dst_item.pk),
                    quantity_delta=qty,
                    transaction_type=TransactionType.TRANSFER_IN,
                    unit_cost=unit_cost,
                    reference_number=movement.movement_number,
                    reason=line.reason or movement.reason,
                    performed_by=user,
                )

            # Stock Reservation
            elif m_type == MovementType.RESERVATION:
                wh = movement.source_warehouse or movement.warehouse
                target_loc = src_loc or movement.source_location
                inv_item = self.inventory_service.get_or_create_inventory_item(
                    tenant=tenant, company=movement.company, warehouse=wh, storage_location=target_loc, medicine=med, batch=batch
                )
                self.inventory_service.reserve_stock(
                    tenant=tenant,
                    inventory_item_id=str(inv_item.pk),
                    requested_quantity=qty,
                    reference_number=movement.movement_number,
                    performed_by=user,
                )

            # Reservation Release
            elif m_type == MovementType.RESERVATION_RELEASE:
                wh = movement.source_warehouse or movement.warehouse
                target_loc = src_loc or movement.source_location
                inv_item = self.inventory_service.get_or_create_inventory_item(
                    tenant=tenant, company=movement.company, warehouse=wh, storage_location=target_loc, medicine=med, batch=batch
                )
                self.inventory_service.release_reservation(
                    tenant=tenant,
                    inventory_item_id=str(inv_item.pk),
                    release_quantity=qty,
                    reference_number=movement.movement_number,
                    performed_by=user,
                )

        movement.mark_completed(user=user)
        logger.info("Processed stock movement %s (%s)", movement.movement_number, m_type)
        return movement

    @transaction.atomic
    def reverse_movement(self, tenant: Any, movement: StockMovement, user: Any | None = None, reason: str = "") -> StockMovement:
        """Create a compensating reversal movement to safely undo a completed stock movement."""
        movement = (
            StockMovement.objects.filter(tenant=tenant, pk=movement.pk)
            .select_for_update()
            .first()
        )
        if not movement:
            raise InvalidMovementStateError("Stock movement does not exist.")

        if movement.movement_status == MovementStatus.REVERSED:
            raise MovementAlreadyReversedError("Stock movement has already been reversed.")
        if movement.movement_status != MovementStatus.COMPLETED:
            raise CannotReverseUnprocessedMovementError("Only completed stock movements can be reversed.")

        # Determine opposing movement type
        reverse_type_map = {
            MovementType.RECEIPT: MovementType.ADJUSTMENT_OUT,
            MovementType.OPENING_BALANCE: MovementType.ADJUSTMENT_OUT,
            MovementType.ADJUSTMENT_IN: MovementType.ADJUSTMENT_OUT,
            MovementType.ADJUSTMENT_OUT: MovementType.ADJUSTMENT_IN,
            MovementType.ISSUE: MovementType.RECEIPT,
            MovementType.SALE: MovementType.SALE_RETURN,
            MovementType.SALE_RETURN: MovementType.SALE,
            MovementType.PURCHASE_RETURN: MovementType.RECEIPT,
            MovementType.TRANSFER_OUT: MovementType.TRANSFER_IN,
            MovementType.TRANSFER_IN: MovementType.TRANSFER_OUT,
            MovementType.RESERVATION: MovementType.RESERVATION_RELEASE,
            MovementType.RESERVATION_RELEASE: MovementType.RESERVATION,
        }
        rev_type = reverse_type_map.get(movement.movement_type, MovementType.CORRECTION)

        # Build reversed lines (swap source and destination locations for transfers)
        reversed_lines = []
        for line in movement.lines.all():
            reversed_lines.append(
                {
                    "medicine": line.medicine,
                    "batch": line.batch,
                    "quantity": line.quantity,
                    "unit": line.unit,
                    "unit_cost": line.unit_cost,
                    "source_location": line.destination_location,
                    "destination_location": line.source_location,
                    "reason": f"Reversal of {movement.movement_number}",
                    "notes": reason or f"Compensating reversal of line {line.id}",
                }
            )

        rev_movement = self.create_movement(
            tenant=tenant,
            company=movement.company,
            branch=movement.branch,
            warehouse=movement.warehouse,
            source_warehouse=movement.destination_warehouse,
            destination_warehouse=movement.source_warehouse,
            source_location=movement.destination_location,
            destination_location=movement.source_location,
            medicine=movement.medicine,
            batch=movement.batch,
            movement_type=rev_type,
            quantity=movement.quantity,
            unit_cost=movement.unit_cost,
            reference_type=ReferenceType.OTHER,
            reference_id=str(movement.id),
            reference_number=movement.movement_number,
            reason=reason or f"Reversal of {movement.movement_number}",
            notes=f"Compensating movement for reversed document {movement.movement_number}",
            performed_by=user,
            lines=reversed_lines,
            auto_process=True,
        )

        rev_movement.is_reversal = True
        rev_movement.reversed_movement = movement
        rev_movement.save(update_fields=["is_reversal", "reversed_movement"])

        movement.movement_status = MovementStatus.REVERSED
        movement.save(update_fields=["movement_status", "updated_at"])

        logger.info("Reversed stock movement %s with compensating movement %s", movement.movement_number, rev_movement.movement_number)
        return rev_movement

    # Operational Conveniences
    def receive_stock(self, tenant: Any, company: Any, warehouse: Any, location: Any, medicine: Any, quantity: Decimal | float | int, *, batch: Any | None = None, unit_cost: Decimal | float | int = Decimal("0.0000"), reference_number: str = "", performed_by: Any = None, idempotency_key: str = "") -> StockMovement:
        return self.create_movement(
            tenant=tenant, company=company, warehouse=warehouse, destination_location=location, medicine=medicine, batch=batch, movement_type=MovementType.RECEIPT, quantity=quantity, unit_cost=unit_cost, reference_number=reference_number, performed_by=performed_by, idempotency_key=idempotency_key, auto_process=True
        )

    def issue_stock(self, tenant: Any, company: Any, warehouse: Any, location: Any, medicine: Any, quantity: Decimal | float | int, *, batch: Any | None = None, reference_number: str = "", performed_by: Any = None, idempotency_key: str = "") -> StockMovement:
        # FEFO fallback if batch is omitted
        if not batch:
            fefo_batches = list(self.batch_selector.get_available_batches_fefo(tenant, str(medicine.pk)))
            if fefo_batches:
                batch = fefo_batches[0]

        return self.create_movement(
            tenant=tenant, company=company, warehouse=warehouse, source_location=location, medicine=medicine, batch=batch, movement_type=MovementType.ISSUE, quantity=quantity, reference_number=reference_number, performed_by=performed_by, idempotency_key=idempotency_key, auto_process=True
        )

    def transfer_stock(self, tenant: Any, company: Any, source_warehouse: Any, destination_warehouse: Any, source_location: Any, destination_location: Any, medicine: Any, quantity: Decimal | float | int, *, batch: Any | None = None, reference_number: str = "", performed_by: Any = None, idempotency_key: str = "") -> StockMovement:
        return self.create_movement(
            tenant=tenant, company=company, warehouse=source_warehouse, source_warehouse=source_warehouse, destination_warehouse=destination_warehouse, source_location=source_location, destination_location=destination_location, medicine=medicine, batch=batch, movement_type=MovementType.TRANSFER_OUT, quantity=quantity, reference_number=reference_number, performed_by=performed_by, idempotency_key=idempotency_key, auto_process=True
        )
