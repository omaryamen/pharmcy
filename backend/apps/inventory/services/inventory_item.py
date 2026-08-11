"""Inventory service handling thread-safe stock position mutations, reservations, quarantines, and auditable transactions."""

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

        item = (
            self.item_repository.filter(tenant=tenant, pk=inventory_item_id)
            .select_for_update()
            .first()
        )
        if not item:
            raise InventoryItemNotFoundError()

        new_on_hand = item.on_hand_quantity + delta
        if new_on_hand < Decimal("0.00"):
            raise NegativeStockForbiddenError(
                f"Adjustment of {delta} resulted in negative stock ({new_on_hand}) for item {item.id}."
            )

        qty_before = item.on_hand_quantity
        item.on_hand_quantity = new_on_hand

        if unit_cost is not None:
            new_u_cost = Decimal(str(unit_cost))
            if new_on_hand > Decimal("0") and delta > Decimal("0"):
                old_val = qty_before * item.average_cost
                new_val = delta * new_u_cost
                item.average_cost = (old_val + new_val) / new_on_hand
            item.last_cost = new_u_cost
            item.unit_cost = new_u_cost

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
            transaction_type=transaction_type,
            quantity=delta,
            unit_cost=item.unit_cost,
            total_cost=abs(delta) * item.unit_cost,
            quantity_before=qty_before,
            quantity_after=new_on_hand,
            reference_number=reference_number,
            performed_by=performed_by,
            notes=notes,
        )

        logger.info("Adjusted stock for item %s by %s. New Total: %s", item.id, delta, item.on_hand_quantity)
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

    @transaction.atomic
    def quarantine_stock(
        self,
        tenant,
        inventory_item_id: str,
        *,
        quarantine_quantity: Decimal | float | int,
        reference_number: str = "",
        performed_by=None,
        notes: str = "",
    ) -> tuple[InventoryItem, InventoryTransaction]:
        """Thread-safe quarantine placement using SELECT FOR UPDATE lock."""
        q_qty = Decimal(str(quarantine_quantity))

        item = (
            self.item_repository.filter(tenant=tenant, pk=inventory_item_id)
            .select_for_update()
            .first()
        )
        if not item:
            raise InventoryItemNotFoundError()

        if item.available_quantity < q_qty:
            raise InsufficientStockError(
                f"Requested quarantine of {q_qty} exceeds available stock ({item.available_quantity}) for {item.medicine.english_name}."
            )

        qty_before = item.on_hand_quantity
        item.quarantine_quantity += q_qty
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
            transaction_type=TransactionType.ADJUSTMENT_DECREASE,
            quantity=q_qty,
            unit_cost=item.unit_cost,
            total_cost=q_qty * item.unit_cost,
            quantity_before=qty_before,
            quantity_after=qty_before,
            reference_number=reference_number,
            performed_by=performed_by,
            notes=notes or "Stock moved to quarantine",
        )

        logger.info("Quarantined %s units of item %s. Quarantine Total: %s", q_qty, item.id, item.quarantine_quantity)
        return item, tx

    @transaction.atomic
    def release_quarantine(
        self,
        tenant,
        inventory_item_id: str,
        *,
        release_quantity: Decimal | float | int,
        reference_number: str = "",
        performed_by=None,
        notes: str = "",
    ) -> tuple[InventoryItem, InventoryTransaction]:
        """Thread-safe quarantine release using SELECT FOR UPDATE lock."""
        rel_qty = Decimal(str(release_quantity))

        item = (
            self.item_repository.filter(tenant=tenant, pk=inventory_item_id)
            .select_for_update()
            .first()
        )
        if not item:
            raise InventoryItemNotFoundError()

        actual_release = min(item.quarantine_quantity, rel_qty)
        qty_before = item.on_hand_quantity
        item.quarantine_quantity -= actual_release
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
            transaction_type=TransactionType.ADJUSTMENT_INCREASE,
            quantity=actual_release,
            unit_cost=item.unit_cost,
            total_cost=actual_release * item.unit_cost,
            quantity_before=qty_before,
            quantity_after=qty_before,
            reference_number=reference_number,
            performed_by=performed_by,
            notes=notes or "Stock released from quarantine",
        )

        logger.info("Released %s units from quarantine for item %s", actual_release, item.id)
        return item, tx
