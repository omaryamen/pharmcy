"""Authoritative domain service for Enterprise Stock Transfer orchestration."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.inventory.models import InventoryItem
from apps.stock_movement.models import MovementType, ReferenceType
from apps.stock_movement.services import StockMovementEngine
from apps.stock_transfer.exceptions import (
    CannotCancelDispatchedTransferError,
    DuplicateTransferOperationError,
    InsufficientTransferStockError,
    InvalidTransferStateError,
    TransferAlreadyCancelledError,
    TransferAlreadyDispatchedError,
    TransferAlreadyReceivedError,
    TransferAlreadyReversedError,
    WrongMedicineReceivedError,
)
from apps.stock_transfer.models import (
    DiscrepancyStatus,
    DiscrepancyType,
    StockTransfer,
    StockTransferDiscrepancy,
    StockTransferHistory,
    StockTransferLine,
    TransferLineStatus,
    TransferPriority,
    TransferStatus,
    TransferType,
)
from apps.stock_transfer.repositories import (
    StockTransferDiscrepancyRepository,
    StockTransferHistoryRepository,
    StockTransferLineRepository,
    StockTransferRepository,
)
from apps.stock_transfer.services.transfer_number_generator import TransferNumberGenerator
from apps.stock_transfer.validators import (
    validate_approval_separation_of_duties,
    validate_batch_eligible_for_transfer,
    validate_non_negative_quantity,
    validate_positive_quantity,
)
from apps.warehouses.models import StorageLocation

logger = logging.getLogger(__name__)


class StockTransferService:
    """Core domain service managing inter-branch and warehouse stock transfers, FEFO picking, dispatching, receiving, discrepancies, and stock movement reconciliation."""

    def __init__(self):
        self.repository = StockTransferRepository()
        self.line_repository = StockTransferLineRepository()
        self.discrepancy_repository = StockTransferDiscrepancyRepository()
        self.history_repository = StockTransferHistoryRepository()
        self.number_generator = TransferNumberGenerator()
        self.movement_engine = StockMovementEngine()

    def _resolve_destination_location(self, tenant: Any, transfer: StockTransfer, line: StockTransferLine, explicit_loc: Any | None = None) -> StorageLocation:
        """Resolve a valid destination storage location belonging to transfer.destination_warehouse."""
        loc = explicit_loc or line.destination_location or transfer.destination_location
        if loc and loc.warehouse_id == transfer.destination_warehouse_id:
            return loc

        fallback = StorageLocation.objects.filter(tenant=tenant, warehouse=transfer.destination_warehouse).first()
        if fallback:
            return fallback

        # If destination warehouse has no locations, create a default location
        return StorageLocation.objects.create(
            tenant=tenant,
            warehouse=transfer.destination_warehouse,
            code=f"MAIN-{transfer.destination_warehouse.code}",
            name=f"Main Storage {transfer.destination_warehouse.name}",
        )

    @transaction.atomic
    def create_transfer(
        self,
        tenant: Any,
        company: Any,
        source_warehouse: Any,
        destination_warehouse: Any,
        lines_data: list[dict[str, Any]],
        *,
        source_branch: Any | None = None,
        destination_branch: Any | None = None,
        source_location: Any | None = None,
        destination_location: Any | None = None,
        transfer_type: str = TransferType.WAREHOUSE_TRANSFER,
        priority: str = TransferPriority.MEDIUM,
        expected_arrival_date: Any | None = None,
        reason: str = "",
        notes: str = "",
        reference_type: str = "",
        reference_id: str = "",
        idempotency_key: str = "",
        user: Any | None = None,
    ) -> StockTransfer:
        """Create a stock transfer header document and associated lines in DRAFT status."""
        if idempotency_key:
            existing = self.repository.find_by_idempotency_key(tenant, idempotency_key)
            if existing:
                logger.info("Found existing stock transfer %s for idempotency_key %s", existing.transfer_number, idempotency_key)
                return existing

        transfer_num = self.number_generator.generate_transfer_number(tenant)

        transfer = self.repository.create(
            tenant=tenant,
            company=company,
            source_branch=source_branch,
            destination_branch=destination_branch,
            source_warehouse=source_warehouse,
            destination_warehouse=destination_warehouse,
            source_location=source_location,
            destination_location=destination_location,
            transfer_number=transfer_num,
            transfer_type=transfer_type,
            priority=priority,
            status=TransferStatus.DRAFT,
            expected_arrival_date=expected_arrival_date,
            reason=reason,
            notes=notes,
            reference_type=reference_type,
            reference_id=reference_id,
            idempotency_key=idempotency_key,
            requested_by=user,
        )

        total_items = 0
        total_requested = Decimal("0.0000")
        total_cost = Decimal("0.0000")

        for line_item in lines_data:
            qty = validate_positive_quantity(line_item["requested_quantity"])
            unit_cost = Decimal(str(line_item.get("unit_cost", "0.0000")))
            line_src_loc = line_item.get("source_location") or source_location

            if not line_src_loc:
                raise InvalidTransferStateError("Each transfer line must specify a valid source location.")

            line_dst_loc = line_item.get("destination_location") or destination_location

            line = self.line_repository.create(
                tenant=tenant,
                stock_transfer=transfer,
                medicine=line_item["medicine"],
                batch=line_item.get("batch"),
                source_location=line_src_loc,
                destination_location=line_dst_loc,
                requested_quantity=qty,
                approved_quantity=qty,
                unit=line_item.get("unit", "Pcs"),
                unit_cost=unit_cost,
                status=TransferLineStatus.PENDING,
                notes=line_item.get("notes", ""),
            )
            line.recalculate_total_cost()
            line.save(update_fields=["total_cost"])

            total_items += 1
            total_requested += qty
            total_cost += line.total_cost

        transfer.total_items = total_items
        transfer.total_requested_quantity = total_requested
        transfer.total_cost = total_cost
        transfer.save(update_fields=["total_items", "total_requested_quantity", "total_cost", "updated_at"])

        self._record_history(tenant, transfer, "CREATED", user, {"transfer_number": transfer_num, "total_items": total_items})
        logger.info("Created stock transfer %s (%s)", transfer_num, transfer_type)
        return transfer

    @transaction.atomic
    def request_transfer(self, tenant: Any, transfer: StockTransfer, user: Any | None = None) -> StockTransfer:
        """Submit a DRAFT transfer document for approval."""
        if transfer.status != TransferStatus.DRAFT:
            raise InvalidTransferStateError(f"Cannot request transfer in status {transfer.status}.")

        now = timezone.now()
        transfer.status = TransferStatus.REQUESTED
        transfer.requested_at = now
        transfer.requested_by = user or transfer.requested_by
        transfer.save(update_fields=["status", "requested_at", "requested_by", "updated_at"])

        self._record_history(tenant, transfer, "REQUESTED", user, {"status": TransferStatus.REQUESTED})
        logger.info("Requested stock transfer %s", transfer.transfer_number)
        return transfer

    @transaction.atomic
    def approve_transfer(
        self,
        tenant: Any,
        transfer: StockTransfer,
        user: Any | None = None,
        approved_lines: list[dict[str, Any]] | None = None,
    ) -> StockTransfer:
        """Approve a requested transfer document, enforcing separation of duties."""
        if transfer.status not in [TransferStatus.REQUESTED, TransferStatus.PENDING_APPROVAL]:
            raise InvalidTransferStateError(f"Cannot approve transfer in status {transfer.status}.")

        validate_approval_separation_of_duties(
            transfer.requested_by, user, is_superuser=getattr(user, "is_superuser", False)
        )

        now = timezone.now()

        if approved_lines:
            line_map = {str(l.pk): l for l in transfer.lines.all()}
            for app_entry in approved_lines:
                line_id = str(app_entry["line_id"])
                if line_id in line_map:
                    line = line_map[line_id]
                    app_qty = validate_non_negative_quantity(app_entry["approved_quantity"])
                    line.approved_quantity = app_qty
                    line.save(update_fields=["approved_quantity", "updated_at"])

        transfer.status = TransferStatus.APPROVED
        transfer.approved_at = now
        transfer.approved_by = user
        transfer.save(update_fields=["status", "approved_at", "approved_by", "updated_at"])

        self._record_history(tenant, transfer, "APPROVED", user, {"approved_by": str(user)})
        logger.info("Approved stock transfer %s", transfer.transfer_number)
        return transfer

    @transaction.atomic
    def pick_transfer(
        self,
        tenant: Any,
        transfer: StockTransfer,
        picking_data: list[dict[str, Any]] | None = None,
        user: Any | None = None,
    ) -> StockTransfer:
        """Perform FEFO-aware stock picking for transfer lines.

        If a batch is not explicitly provided on a line, automatically selects
        valid non-expired batches according to FEFO rules.
        """
        if transfer.status not in [TransferStatus.APPROVED, TransferStatus.PICKING]:
            raise InvalidTransferStateError(f"Cannot pick stock for transfer in status {transfer.status}.")

        transfer.status = TransferStatus.PICKING
        transfer.save(update_fields=["status", "updated_at"])

        lines = list(transfer.lines.select_related("medicine", "batch", "source_location"))

        if picking_data:
            picking_map = {str(p["line_id"]): p for p in picking_data if "line_id" in p}
            for line in lines:
                p_entry = picking_map.get(str(line.pk))
                if p_entry:
                    pick_qty = validate_non_negative_quantity(p_entry["picked_quantity"])
                    if "batch" in p_entry and p_entry["batch"]:
                        validate_batch_eligible_for_transfer(p_entry["batch"])
                        line.batch = p_entry["batch"]

                    line.picked_quantity = pick_qty
                    line.status = TransferLineStatus.PICKED
                    line.save(update_fields=["batch", "picked_quantity", "status", "updated_at"])
        else:
            # Auto-FEFO picking logic for each line
            for line in lines:
                if line.batch:
                    validate_batch_eligible_for_transfer(line.batch)
                    line.picked_quantity = line.approved_quantity
                else:
                    # Search FEFO eligible active inventory items
                    inv_items = (
                        InventoryItem.objects.filter(
                            tenant=tenant,
                            warehouse=transfer.source_warehouse,
                            storage_location=line.source_location,
                            medicine=line.medicine,
                            on_hand_quantity__gt=Decimal("0"),
                            batch__status="active",
                            batch__expiry_date__gt=timezone.now().date(),
                        )
                        .select_related("batch")
                        .order_by("batch__expiry_date")
                    )

                    remaining_needed = line.approved_quantity
                    for inv_item in inv_items:
                        if remaining_needed <= Decimal("0"):
                            break

                        avail = inv_item.available_quantity
                        if avail > Decimal("0"):
                            line.batch = inv_item.batch
                            pick_from_batch = min(avail, remaining_needed)
                            line.picked_quantity = pick_from_batch
                            remaining_needed -= pick_from_batch

                line.status = TransferLineStatus.PICKED
                line.save(update_fields=["batch", "picked_quantity", "status", "updated_at"])

        transfer.status = TransferStatus.READY_FOR_DISPATCH
        transfer.save(update_fields=["status", "updated_at"])

        self._record_history(tenant, transfer, "PICKED", user, {"lines_picked": len(lines)})
        logger.info("Picked stock for transfer %s", transfer.transfer_number)
        return transfer

    @transaction.atomic
    def dispatch_transfer(
        self,
        tenant: Any,
        transfer: StockTransfer,
        dispatch_lines: list[dict[str, Any]] | None = None,
        user: Any | None = None,
        idempotency_key: str = "",
    ) -> StockTransfer:
        """Dispatch physical stock transfer by moving stock out of source location to destination location via StockMovementEngine."""
        transfer = (
            StockTransfer.objects.filter(tenant=tenant, pk=transfer.pk)
            .select_for_update()
            .first()
        )
        if not transfer:
            raise InvalidTransferStateError("Stock transfer does not exist.")

        if transfer.status == TransferStatus.DISPATCHED or transfer.status == TransferStatus.IN_TRANSIT:
            logger.info("Stock transfer %s is already dispatched.", transfer.transfer_number)
            return transfer

        if transfer.status not in [TransferStatus.APPROVED, TransferStatus.PICKING, TransferStatus.READY_FOR_DISPATCH]:
            raise InvalidTransferStateError(f"Cannot dispatch stock transfer in status {transfer.status}.")

        now = timezone.now()
        lines = list(transfer.lines.select_related("medicine", "batch", "source_location", "destination_location"))

        if dispatch_lines:
            dispatch_map = {str(d["line_id"]): d for d in dispatch_lines if "line_id" in d}
            for line in lines:
                d_entry = dispatch_map.get(str(line.pk))
                if d_entry:
                    line.dispatched_quantity = validate_non_negative_quantity(d_entry["dispatched_quantity"])
                else:
                    line.dispatched_quantity = line.picked_quantity or line.approved_quantity
        else:
            for line in lines:
                line.dispatched_quantity = line.picked_quantity if line.picked_quantity > Decimal("0") else line.approved_quantity

        total_dispatched = Decimal("0.0000")

        # Execute double-entry StockMovement for each line
        for line in lines:
            if line.dispatched_quantity <= Decimal("0"):
                continue

            if line.batch:
                validate_batch_eligible_for_transfer(line.batch)

            dest_loc = self._resolve_destination_location(tenant, transfer, line)

            # Atomic double-entry transfer via StockMovementEngine
            self.movement_engine.create_movement(
                tenant=tenant,
                company=transfer.company,
                branch=transfer.source_branch,
                warehouse=transfer.source_warehouse,
                source_warehouse=transfer.source_warehouse,
                destination_warehouse=transfer.destination_warehouse,
                source_location=line.source_location,
                destination_location=dest_loc,
                medicine=line.medicine,
                batch=line.batch,
                movement_type=MovementType.TRANSFER_OUT,
                quantity=line.dispatched_quantity,
                unit_cost=line.unit_cost,
                reference_type=ReferenceType.OTHER,
                reference_id=str(transfer.pk),
                reference_number=transfer.transfer_number,
                reason=f"Dispatch for transfer {transfer.transfer_number}",
                performed_by=user,
                auto_process=True,
            )

            line.destination_location = dest_loc
            line.status = TransferLineStatus.DISPATCHED
            line.recalculate_total_cost()
            line.save(update_fields=["dispatched_quantity", "destination_location", "status", "total_cost", "updated_at"])

            total_dispatched += line.dispatched_quantity

        transfer.status = TransferStatus.IN_TRANSIT
        transfer.dispatched_at = now
        transfer.dispatched_by = user
        transfer.total_dispatched_quantity = total_dispatched
        transfer.save(update_fields=["status", "dispatched_at", "dispatched_by", "total_dispatched_quantity", "updated_at"])

        self._record_history(tenant, transfer, "DISPATCHED", user, {"total_dispatched_quantity": str(total_dispatched)})
        logger.info("Dispatched stock transfer %s", transfer.transfer_number)
        return transfer

    @transaction.atomic
    def receive_transfer(
        self,
        tenant: Any,
        transfer: StockTransfer,
        receive_lines_data: list[dict[str, Any]],
        user: Any | None = None,
    ) -> StockTransfer:
        """Receive physical stock transfer at destination, handling partial receipt, damages, wrong batch, or wrong medicine discrepancies."""
        transfer = (
            StockTransfer.objects.filter(tenant=tenant, pk=transfer.pk)
            .select_for_update()
            .first()
        )
        if not transfer:
            raise InvalidTransferStateError("Stock transfer does not exist.")

        if transfer.status in [TransferStatus.RECEIVED, TransferStatus.CLOSED]:
            logger.info("Transfer %s is already received/closed. Returning document idempotently.", transfer.transfer_number)
            return transfer

        if transfer.status not in [TransferStatus.DISPATCHED, TransferStatus.IN_TRANSIT, TransferStatus.PARTIALLY_RECEIVED, TransferStatus.DISCREPANCY]:
            raise InvalidTransferStateError(f"Cannot receive transfer in status {transfer.status}.")

        now = timezone.now()
        lines = list(transfer.lines.select_related("medicine", "batch", "source_location", "destination_location"))
        line_map = {str(l.pk): l for l in lines}

        total_received = Decimal("0.0000")
        has_any_discrepancy = False

        for r_data in receive_lines_data:
            line_id = str(r_data["line_id"])
            if line_id not in line_map:
                continue

            line = line_map[line_id]
            rx_qty = validate_non_negative_quantity(r_data.get("received_quantity", "0"))
            dmg_qty = validate_non_negative_quantity(r_data.get("damaged_quantity", "0"))
            rej_qty = validate_non_negative_quantity(r_data.get("rejected_quantity", "0"))

            dest_loc = self._resolve_destination_location(tenant, transfer, line, r_data.get("destination_location"))

            rx_medicine = r_data.get("received_medicine") or line.medicine
            rx_batch = r_data.get("received_batch") or line.batch

            # Check 1: Wrong Medicine Detection
            if rx_medicine.pk != line.medicine.pk:
                has_any_discrepancy = True
                disc_num = self.number_generator.generate_discrepancy_number(tenant)
                self.discrepancy_repository.create(
                    tenant=tenant,
                    stock_transfer=transfer,
                    transfer_line=line,
                    discrepancy_number=disc_num,
                    discrepancy_type=DiscrepancyType.WRONG_MEDICINE,
                    expected_quantity=line.dispatched_quantity,
                    actual_quantity=rx_qty,
                    difference_quantity=line.dispatched_quantity - rx_qty,
                    expected_medicine=line.medicine,
                    received_medicine=rx_medicine,
                    reason=f"Wrong medicine received on transfer line {line.pk}",
                    reported_by=user,
                    status=DiscrepancyStatus.REPORTED,
                )
                line.status = TransferLineStatus.REJECTED
                line.save(update_fields=["status", "updated_at"])
                continue

            # Check 2: Wrong Batch Detection
            if rx_batch and line.batch and rx_batch.pk != line.batch.pk:
                has_any_discrepancy = True
                disc_num = self.number_generator.generate_discrepancy_number(tenant)
                self.discrepancy_repository.create(
                    tenant=tenant,
                    stock_transfer=transfer,
                    transfer_line=line,
                    discrepancy_number=disc_num,
                    discrepancy_type=DiscrepancyType.WRONG_BATCH,
                    expected_quantity=line.dispatched_quantity,
                    actual_quantity=rx_qty,
                    difference_quantity=line.dispatched_quantity - rx_qty,
                    expected_batch=line.batch,
                    received_batch=rx_batch,
                    reason=f"Wrong batch received on transfer line {line.pk}",
                    reported_by=user,
                    status=DiscrepancyStatus.REPORTED,
                )

            # Process damaged stock via StockMovementEngine (DAMAGE at destination location)
            if dmg_qty > Decimal("0"):
                has_any_discrepancy = True
                self.movement_engine.create_movement(
                    tenant=tenant,
                    company=transfer.company,
                    branch=transfer.destination_branch,
                    warehouse=transfer.destination_warehouse,
                    source_location=dest_loc,
                    medicine=rx_medicine,
                    batch=rx_batch,
                    movement_type=MovementType.DAMAGE,
                    quantity=dmg_qty,
                    unit_cost=line.unit_cost,
                    reference_type=ReferenceType.OTHER,
                    reference_id=str(transfer.pk),
                    reference_number=transfer.transfer_number,
                    reason=f"Damaged in-transit receipt for {transfer.transfer_number}",
                    performed_by=user,
                    auto_process=True,
                )
                disc_num = self.number_generator.generate_discrepancy_number(tenant)
                self.discrepancy_repository.create(
                    tenant=tenant,
                    stock_transfer=transfer,
                    transfer_line=line,
                    discrepancy_number=disc_num,
                    discrepancy_type=DiscrepancyType.DAMAGE,
                    expected_quantity=line.dispatched_quantity,
                    actual_quantity=rx_qty,
                    difference_quantity=dmg_qty,
                    reason=r_data.get("damage_reason", f"Goods damaged during transfer {transfer.transfer_number}"),
                    reported_by=user,
                    status=DiscrepancyStatus.REPORTED,
                )

            # Check quantity discrepancy (shortage / overage)
            net_accounted = rx_qty + dmg_qty + rej_qty
            if net_accounted != line.dispatched_quantity:
                has_any_discrepancy = True
                diff = rx_qty - line.dispatched_quantity
                disc_type = DiscrepancyType.SHORTAGE if diff < Decimal("0") else DiscrepancyType.OVERAGE
                disc_num = self.number_generator.generate_discrepancy_number(tenant)
                self.discrepancy_repository.create(
                    tenant=tenant,
                    stock_transfer=transfer,
                    transfer_line=line,
                    discrepancy_number=disc_num,
                    discrepancy_type=disc_type,
                    expected_quantity=line.dispatched_quantity,
                    actual_quantity=rx_qty,
                    difference_quantity=abs(diff),
                    reason=f"Quantity discrepancy on line {line.pk}: dispatched {line.dispatched_quantity}, received {rx_qty}",
                    reported_by=user,
                    status=DiscrepancyStatus.REPORTED,
                )

                if diff < Decimal("0"):
                    # Shortage: deduct missing difference from destination location via ADJUSTMENT_OUT
                    self.movement_engine.create_movement(
                        tenant=tenant,
                        company=transfer.company,
                        branch=transfer.destination_branch,
                        warehouse=transfer.destination_warehouse,
                        source_location=dest_loc,
                        medicine=rx_medicine,
                        batch=rx_batch,
                        movement_type=MovementType.ADJUSTMENT_OUT,
                        quantity=abs(diff),
                        unit_cost=line.unit_cost,
                        reference_type=ReferenceType.OTHER,
                        reference_id=str(transfer.pk),
                        reference_number=transfer.transfer_number,
                        reason=f"Shortage discrepancy for transfer {transfer.transfer_number}",
                        performed_by=user,
                        auto_process=True,
                    )
                elif diff > Decimal("0"):
                    # Overage: add extra difference to destination location via ADJUSTMENT_IN
                    self.movement_engine.create_movement(
                        tenant=tenant,
                        company=transfer.company,
                        branch=transfer.destination_branch,
                        warehouse=transfer.destination_warehouse,
                        destination_location=dest_loc,
                        medicine=rx_medicine,
                        batch=rx_batch,
                        movement_type=MovementType.ADJUSTMENT_IN,
                        quantity=diff,
                        unit_cost=line.unit_cost,
                        reference_type=ReferenceType.OTHER,
                        reference_id=str(transfer.pk),
                        reference_number=transfer.transfer_number,
                        reason=f"Overage discrepancy for transfer {transfer.transfer_number}",
                        performed_by=user,
                        auto_process=True,
                    )

            line.received_quantity = rx_qty
            line.damaged_quantity = dmg_qty
            line.rejected_quantity = rej_qty
            line.destination_location = dest_loc
            line.status = TransferLineStatus.RECEIVED if not has_any_discrepancy else TransferLineStatus.DISCREPANCY
            line.save(update_fields=["received_quantity", "damaged_quantity", "rejected_quantity", "destination_location", "status", "updated_at"])

            total_received += rx_qty

        transfer.received_at = now
        transfer.received_by = user
        transfer.actual_arrival_date = now.date()
        transfer.total_received_quantity = total_received
        transfer.has_discrepancy = has_any_discrepancy

        if has_any_discrepancy:
            transfer.status = TransferStatus.DISCREPANCY
        elif total_received < transfer.total_dispatched_quantity:
            transfer.status = TransferStatus.PARTIALLY_RECEIVED
        else:
            transfer.status = TransferStatus.RECEIVED

        transfer.save(update_fields=["received_at", "received_by", "actual_arrival_date", "total_received_quantity", "has_discrepancy", "status", "updated_at"])

        self._record_history(tenant, transfer, "RECEIVED", user, {"total_received_quantity": str(total_received), "has_discrepancy": has_any_discrepancy})
        logger.info("Received stock transfer %s (Discrepancies=%s)", transfer.transfer_number, has_any_discrepancy)
        return transfer

    @transaction.atomic
    def reject_transfer(self, tenant: Any, transfer: StockTransfer, reason: str, user: Any | None = None) -> StockTransfer:
        """Reject a requested transfer prior to dispatch."""
        if transfer.status not in [TransferStatus.REQUESTED, TransferStatus.PENDING_APPROVAL]:
            raise InvalidTransferStateError(f"Cannot reject transfer in status {transfer.status}.")

        transfer.status = TransferStatus.REJECTED
        transfer.reason = reason
        transfer.save(update_fields=["status", "reason", "updated_at"])

        self._record_history(tenant, transfer, "REJECTED", user, {"reason": reason})
        logger.info("Rejected stock transfer %s", transfer.transfer_number)
        return transfer

    @transaction.atomic
    def cancel_transfer(self, tenant: Any, transfer: StockTransfer, reason: str, user: Any | None = None) -> StockTransfer:
        """Cancel an un-dispatched transfer."""
        if transfer.status in [TransferStatus.DISPATCHED, TransferStatus.IN_TRANSIT, TransferStatus.RECEIVED, TransferStatus.CLOSED]:
            raise CannotCancelDispatchedTransferError()

        if transfer.status == TransferStatus.CANCELLED:
            raise TransferAlreadyCancelledError()

        transfer.status = TransferStatus.CANCELLED
        transfer.cancelled_at = timezone.now()
        transfer.cancelled_by = user
        transfer.reason = reason
        transfer.save(update_fields=["status", "cancelled_at", "cancelled_by", "reason", "updated_at"])

        self._record_history(tenant, transfer, "CANCELLED", user, {"reason": reason})
        logger.info("Cancelled stock transfer %s", transfer.transfer_number)
        return transfer

    @transaction.atomic
    def reverse_transfer(self, tenant: Any, transfer: StockTransfer, reason: str, user: Any | None = None) -> StockTransfer:
        """Execute a compensating reversal for a dispatched/received transfer via StockMovementEngine."""
        transfer = (
            StockTransfer.objects.filter(tenant=tenant, pk=transfer.pk)
            .select_for_update()
            .first()
        )
        if not transfer:
            raise InvalidTransferStateError("Stock transfer does not exist.")

        if transfer.status == TransferStatus.CANCELLED and "REVERSED" in transfer.notes:
            raise TransferAlreadyReversedError()

        if transfer.status not in [TransferStatus.DISPATCHED, TransferStatus.IN_TRANSIT, TransferStatus.RECEIVED, TransferStatus.CLOSED, TransferStatus.DISCREPANCY, TransferStatus.PARTIALLY_RECEIVED]:
            raise InvalidTransferStateError(f"Cannot reverse stock transfer in status {transfer.status}.")

        now = timezone.now()
        lines = list(transfer.lines.select_related("medicine", "batch", "source_location", "destination_location"))

        for line in lines:
            dest_loc = self._resolve_destination_location(tenant, transfer, line)

            if line.dispatched_quantity > Decimal("0"):
                # Reversal: Atomic double-entry transfer moving stock back from destination location to source location
                self.movement_engine.create_movement(
                    tenant=tenant,
                    company=transfer.company,
                    branch=transfer.source_branch,
                    warehouse=transfer.destination_warehouse,
                    source_warehouse=transfer.destination_warehouse,
                    destination_warehouse=transfer.source_warehouse,
                    source_location=dest_loc,
                    destination_location=line.source_location,
                    medicine=line.medicine,
                    batch=line.batch,
                    movement_type=MovementType.TRANSFER_OUT,
                    quantity=line.dispatched_quantity,
                    unit_cost=line.unit_cost,
                    reference_type=ReferenceType.OTHER,
                    reference_id=str(transfer.pk),
                    reference_number=f"REV-{transfer.transfer_number}",
                    reason=f"Reversal of transfer {transfer.transfer_number}: {reason}",
                    performed_by=user,
                    auto_process=True,
                )

        transfer.status = TransferStatus.CANCELLED
        transfer.notes = f"{transfer.notes} [REVERSED on {now.isoformat()}: {reason}]"
        transfer.save(update_fields=["status", "notes", "updated_at"])

        self._record_history(tenant, transfer, "REVERSED", user, {"reason": reason})
        logger.info("Reversed stock transfer %s cleanly via StockMovementEngine", transfer.transfer_number)
        return transfer

    @transaction.atomic
    def reconcile_discrepancy(
        self,
        tenant: Any,
        discrepancy: StockTransferDiscrepancy,
        resolution: str,
        user: Any | None = None,
    ) -> StockTransferDiscrepancy:
        """Resolve a reported transfer discrepancy."""
        if discrepancy.status == DiscrepancyStatus.RESOLVED:
            return discrepancy

        now = timezone.now()
        discrepancy.status = DiscrepancyStatus.RESOLVED
        discrepancy.resolution = resolution
        discrepancy.reviewed_by = user
        discrepancy.resolution_date = now
        discrepancy.save(update_fields=["status", "resolution", "reviewed_by", "resolution_date", "updated_at"])

        self._record_history(
            tenant, discrepancy.stock_transfer, "DISCREPANCY_RESOLVED", user, {"discrepancy_number": discrepancy.discrepancy_number, "resolution": resolution}
        )
        logger.info("Resolved discrepancy %s for transfer %s", discrepancy.discrepancy_number, discrepancy.stock_transfer.transfer_number)
        return discrepancy

    def _record_history(self, tenant: Any, stock_transfer: StockTransfer, event_type: str, user: Any | None, details: dict[str, Any]) -> None:
        StockTransferHistory.objects.create(
            tenant=tenant,
            stock_transfer=stock_transfer,
            event_type=event_type,
            performed_by=user,
            details=details,
        )
