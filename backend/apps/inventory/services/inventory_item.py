"""Inventory service handling thread-safe stock position mutations, reservations, and auditable transactions."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.inventory.exceptions import (
    InsufficientStockError,
    InventoryItemNotFoundError,
    NegativeStockForbiddenError,
)
from apps.inventory.models import (
    AdjustmentReason,
    InventoryItem,
    InventoryStatus,
    InventoryTransaction,
    TransactionType,
)
from apps.inventory.repositories import InventoryItemRepository, InventoryTransactionRepository
from apps.inventory.validators import validate_inventory_batch, validate_inventory_location

logger = logging.getLogger(__name__)


class InventoryService:
    def __init__(self) -> None:
        self.item_repository = InventoryItemRepository()
        self.transaction_repository = InventoryTransactionRepository()

    @transaction.atomic
    def get_or_create_inventory_item(
        self,
        tenant,
        company,
        warehouse,
        storage_location,
        medicine,
        batch,
        *,
        branch=None,
        unit_cost=Decimal("0.0000"),
        selling_price=Decimal("0.0000"),
        min_quantity=Decimal("0.00"),
        max_quantity=Decimal("0.00"),
        reorder_point=Decimal("0.00"),
    ) -> InventoryItem:
        validate_inventory_location(storage_location, warehouse)
        validate_inventory_batch(batch, medicine)

        item = self.item_repository.get_exact_stock_position(
            tenant=tenant,
            warehouse_id=warehouse.id,
            storage_location_id=storage_location.id,
            medicine_id=medicine.id,
            batch_id=batch.id if batch else None,
        )

        if not item:
            item = self.item_repository.create(
                tenant=tenant,
                company=company,
                branch=branch or warehouse.branch,
                warehouse=warehouse,
                storage_location=storage_location,
                medicine=medicine,
                batch=batch,
                status=InventoryStatus.AVAILABLE,
                on_hand_quantity=Decimal("0.00"),
                reserved_quantity=Decimal("0.00"),
                damaged_quantity=Decimal("0.00"),
                quarantine_quantity=Decimal("0.00"),
                unit_cost=Decimal(str(unit_cost)),
                average_cost=Decimal(str(unit_cost)),
                last_cost=Decimal(str(unit_cost)),
                selling_price=Decimal(str(selling_price)),
                min_quantity=Decimal(str(min_quantity)),
                max_quantity=Decimal(str(max_quantity)),
                reorder_point=Decimal(str(reorder_point)),
            )

        return item

    @transaction.atomic
    def adjust_quantity(
        self,
        tenant,
        inventory_item_id: str,
        *,
        quantity_delta: Decimal | float | int,
        transaction_type: str = TransactionType.ADJUSTMENT_INCREASE,
        reason: str = AdjustmentReason.CORRECTION,
        reference_number: str = "",
        unit_cost: Decimal | float | int | None = None,
        performed_by=None,
        notes: str = "",
    ) -> tuple[InventoryItem, InventoryTransaction]:
        """Thread-safe quantity adjustment using SELECT FOR UPDATE lock."""
        delta = Decimal(str(quantity_delta))

        # Acquire pessimistic DB row lock to prevent race conditions
        item = (
            self.item_repository.filter(tenant=tenant, pk=inventory_item_id)
            .select_for_update()
            .first()
        )
        if not item:
            raise InventoryItemNotFoundError()

        qty_before = item.on_hand_quantity
        qty_after = qty_before + delta

        if qty_after < Decimal("0.00"):
            raise NegativeStockForbiddenError(
                f"Cannot adjust stock by {delta} as it results in negative stock ({qty_after}) for {item.medicine.english_name}."
            )

        # Update cost if provided
        cost = Decimal(str(unit_cost)) if unit_cost is not None else item.unit_cost
        if delta > Decimal("0.00") and unit_cost is not None:
            # Weighted average cost update calculation
            total_current_val = qty_before * item.average_cost
            new_incoming_val = delta * cost
            if qty_after > Decimal("0.00"):
                item.average_cost = (total_current_val + new_incoming_val) / qty_after
            item.last_cost = cost

        item.on_hand_quantity = qty_after
        item.last_movement_date = timezone.now()
        item.save()

        total_tx_cost = abs(delta) * cost
        tx = self.transaction_repository.create(
            tenant=tenant,
            company=item.company,
            branch=item.branch,
            warehouse=item.warehouse,
            storage_location=item.storage_location,
            medicine=item.medicine,
            batch=item.batch,
            inventory_item=item,
            transaction_type=transaction_type,
            quantity=delta,
            unit_cost=cost,
            total_cost=total_tx_cost,
            quantity_before=qty_before,
            quantity_after=qty_after,
            reference_number=reference_number,
            reason=reason,
            performed_by=performed_by,
            notes=notes,
        )

        logger.info("Adjusted inventory item %s by %s. New On-Hand: %s", item.id, delta, qty_after)
        return item, tx

    @transaction.atomic
    def reserve_stock(
        self,
        tenant,
        inventory_item_id: str,
        *,
        requested_quantity: Decimal | float | int,
        reference_number: str = "",
        performed_by=None,
        notes: str = "",
    ) -> tuple[InventoryItem, InventoryTransaction]:
        """Thread-safe stock reservation using SELECT FOR UPDATE lock."""
        req_qty = Decimal(str(requested_quantity))
        if req_qty <= Decimal("0.00"):
            raise NegativeStockForbiddenError("Reserved quantity must be greater than zero.")

        item = (
            self.item_repository.filter(tenant=tenant, pk=inventory_item_id)
            .select_for_update()
            .first()
        )
        if not item:
            raise InventoryItemNotFoundError()

        if item.available_quantity < req_qty:
            raise InsufficientStockError(
                f"Requested reservation of {req_qty} exceeds available stock ({item.available_quantity}) for {item.medicine.english_name}."
            )

        qty_before = item.on_hand_quantity
        item.reserved_quantity += req_qty
        item.save()

        tx = self.transaction_repository.create(
            tenant=tenant,
            company=item.company,
            branch=item.branch,
            warehouse=item.warehouse,
            storage_location=item.storage_location,
            medicine=item.medicine,
            batch=item.batch,
            inventory_item=item,
            transaction_type=TransactionType.RESERVATION,
            quantity=req_qty,
            unit_cost=item.unit_cost,
            total_cost=req_qty * item.unit_cost,
            quantity_before=qty_before,
            quantity_after=qty_before,
            reference_number=reference_number,
            performed_by=performed_by,
            notes=notes,
        )

        logger.info("Reserved %s units of item %s. Reserved Total: %s", req_qty, item.id, item.reserved_quantity)
        return item, tx

    @transaction.atomic
    def release_reservation(
        self,
        tenant,
        inventory_item_id: str,
        *,
        release_quantity: Decimal | float | int,
        reference_number: str = "",
        performed_by=None,
        notes: str = "",
    ) -> tuple[InventoryItem, InventoryTransaction]:
        """Thread-safe reservation release using SELECT FOR UPDATE lock."""
        rel_qty = Decimal(str(release_quantity))

        item = (
            self.item_repository.filter(tenant=tenant, pk=inventory_item_id)
            .select_for_update()
            .first()
        )
        if not item:
            raise InventoryItemNotFoundError()

        actual_release = min(item.reserved_quantity, rel_qty)
        qty_before = item.on_hand_quantity
        item.reserved_quantity -= actual_release
        item.save()

        tx = self.transaction_repository.create(
            tenant=tenant,
            company=item.company,
            branch=item.branch,
            warehouse=item.warehouse,
            storage_location=item.storage_location,
            medicine=item.medicine,
            batch=item.batch,
            inventory_item=item,
            transaction_type=TransactionType.RELEASE_RESERVATION,
            quantity=-actual_release,
            unit_cost=item.unit_cost,
            total_cost=actual_release * item.unit_cost,
            quantity_before=qty_before,
            quantity_after=qty_before,
            reference_number=reference_number,
            performed_by=performed_by,
            notes=notes,
        )

        logger.info("Released reservation of %s units from item %s", actual_release, item.id)
        return item, tx
