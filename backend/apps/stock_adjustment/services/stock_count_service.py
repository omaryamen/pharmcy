"""Authoritative domain service for Enterprise Stock Count management and reconciliation."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.inventory.models import InventoryItem
from apps.stock_adjustment.exceptions import (
    CountAlreadyCancelledError,
    CountAlreadyReconciledError,
    CountAlreadySubmittedError,
    DuplicateReconciliationError,
    InvalidCountStateError,
    SelfApprovalForbiddenError,
    StockAdjustmentError,
    VarianceExceedsThresholdError,
)
from apps.stock_adjustment.models import (
    CountScopeType,
    CountStatus,
    CountType,
    RecountStatus,
    SessionStatus,
    StockCount,
    StockCountHistory,
    StockCountLine,
    StockCountRecount,
    StockCountSession,
    VarianceDirection,
)
from apps.stock_adjustment.repositories import (
    StockCountLineRepository,
    StockCountRecountRepository,
    StockCountRepository,
    StockCountSessionRepository,
)
from apps.stock_adjustment.services.count_number_generator import CountNumberGenerator
from apps.stock_adjustment.validators import validate_non_negative_quantity, validate_user_not_same_as_counter
from apps.stock_movement.models import MovementType, ReferenceType
from apps.stock_movement.services import StockMovementEngine

logger = logging.getLogger(__name__)


class StockCountService:
    """Core domain service managing the lifecycle, variance detection, recount, approval, and reconciliation of stock counts."""

    def __init__(self):
        self.repository = StockCountRepository()
        self.line_repository = StockCountLineRepository()
        self.session_repository = StockCountSessionRepository()
        self.recount_repository = StockCountRecountRepository()
        self.number_generator = CountNumberGenerator()
        self.movement_engine = StockMovementEngine()

    @transaction.atomic
    def create_stock_count(
        self,
        tenant: Any,
        company: Any,
        warehouse: Any,
        count_type: str,
        *,
        branch: Any | None = None,
        storage_location: Any | None = None,
        count_scope_type: str = CountScopeType.WAREHOUSE,
        scope_filter: dict[str, Any] | None = None,
        is_blind_count: bool = False,
        freeze_inventory: bool = False,
        reason: str = "",
        notes: str = "",
        idempotency_key: str = "",
        created_by: Any | None = None,
    ) -> StockCount:
        """Create a stock count header document."""
        if idempotency_key:
            existing = self.repository.find_by_idempotency_key(tenant, idempotency_key)
            if existing:
                logger.info("Found existing stock count %s for idempotency_key %s", existing.count_number, idempotency_key)
                return existing

        count_num = self.number_generator.generate_count_number(tenant)

        stock_count = self.repository.create(
            tenant=tenant,
            company=company,
            branch=branch,
            warehouse=warehouse,
            storage_location=storage_location,
            count_number=count_num,
            count_type=count_type,
            count_status=CountStatus.DRAFT,
            count_scope_type=count_scope_type,
            scope_filter=scope_filter or {},
            is_blind_count=is_blind_count or (count_type == CountType.BLIND_COUNT),
            freeze_inventory=freeze_inventory,
            reason=reason,
            notes=notes,
            idempotency_key=idempotency_key,
            created_by=created_by,
        )

        self._record_history(tenant, stock_count, "CREATED", created_by, {"count_number": count_num, "count_type": count_type})
        logger.info("Created stock count %s (%s)", count_num, count_type)
        return stock_count

    @transaction.atomic
    def start_stock_count(self, tenant: Any, stock_count: StockCount, user: Any | None = None) -> StockCount:
        """Start count session and snapshot system inventory quantities for the specified count scope."""
        if stock_count.count_status not in [CountStatus.DRAFT, CountStatus.PLANNED]:
            raise InvalidCountStateError(f"Cannot start stock count in status {stock_count.count_status}.")

        now = timezone.now()
        stock_count.snapshot_at = now
        stock_count.started_at = now
        stock_count.started_by = user
        stock_count.count_status = CountStatus.IN_PROGRESS
        stock_count.save(update_fields=["snapshot_at", "started_at", "started_by", "count_status", "updated_at"])

        # Query live InventoryItem records matching count scope
        items_qs = InventoryItem.objects.filter(tenant=tenant, warehouse=stock_count.warehouse)
        if stock_count.storage_location:
            items_qs = items_qs.filter(storage_location=stock_count.storage_location)

        scope_filter = stock_count.scope_filter or {}
        if "medicine_id" in scope_filter:
            items_qs = items_qs.filter(medicine_id=scope_filter["medicine_id"])
        if "medicine_ids" in scope_filter:
            items_qs = items_qs.filter(medicine_id__in=scope_filter["medicine_ids"])
        if "batch_id" in scope_filter:
            items_qs = items_qs.filter(batch_id=scope_filter["batch_id"])
        if "category_id" in scope_filter:
            items_qs = items_qs.filter(medicine__category_id=scope_filter["category_id"])

        items = list(items_qs.select_related("medicine", "batch", "storage_location"))

        for item in items:
            self.line_repository.create(
                tenant=tenant,
                stock_count=stock_count,
                medicine=item.medicine,
                batch=item.batch,
                storage_location=item.storage_location,
                unit_cost=item.unit_cost,
                snapshot_quantity=item.on_hand_quantity,
                counted_quantity=Decimal("0.0000"),
            )

        self._record_history(tenant, stock_count, "STARTED", user, {"snapshot_items_count": len(items)})
        logger.info("Started stock count %s with %d snapshot lines", stock_count.count_number, len(items))
        return stock_count

    @transaction.atomic
    def record_count_lines(
        self,
        tenant: Any,
        stock_count: StockCount,
        lines_data: list[dict[str, Any]],
        user: Any | None = None,
    ) -> StockCount:
        """Record physical counted quantities for lines in a stock count.

        Each entry may identify a line by ``line_id`` (UUID) or by the
        combination of ``medicine_id``, ``batch_id`` and ``storage_location_id``.
        If no matching line exists a new one is created (ad-hoc line entry).
        """
        if stock_count.count_status not in [CountStatus.IN_PROGRESS, CountStatus.RECOUNT_REQUIRED]:
            raise InvalidCountStateError(f"Cannot record count lines when count status is {stock_count.count_status}.")

        now = timezone.now()

        for entry in lines_data:
            counted_qty = validate_non_negative_quantity(entry["counted_quantity"])
            unit_cost = Decimal(str(entry.get("unit_cost", "0.0000")))
            notes_text = entry.get("notes", "")

            line = None

            # Strategy 1: lookup by explicit line_id
            if "line_id" in entry:
                line = StockCountLine.objects.filter(tenant=tenant, stock_count=stock_count, pk=entry["line_id"]).first()

            # Strategy 2: lookup by medicine + batch + location composite key
            if line is None and "medicine_id" in entry:
                filter_kwargs: dict[str, Any] = {
                    "tenant": tenant,
                    "stock_count": stock_count,
                    "medicine_id": entry["medicine_id"],
                    "storage_location_id": entry.get("storage_location_id"),
                }
                if entry.get("batch_id"):
                    filter_kwargs["batch_id"] = entry["batch_id"]
                else:
                    filter_kwargs["batch__isnull"] = True

                line = StockCountLine.objects.filter(**filter_kwargs).first()

                # Create an ad-hoc line if not yet snapshotted
                if line is None:
                    line = StockCountLine.objects.create(
                        tenant=tenant,
                        stock_count=stock_count,
                        medicine_id=entry["medicine_id"],
                        batch_id=entry.get("batch_id"),
                        storage_location_id=entry.get("storage_location_id"),
                        snapshot_quantity=Decimal("0.0000"),
                        counted_quantity=counted_qty,
                        unit_cost=unit_cost,
                        counted_by=user,
                        notes=notes_text,
                    )
                    continue

            if line is not None:
                line.counted_quantity = counted_qty
                line.counted_by = user
                if unit_cost:
                    line.unit_cost = unit_cost
                if notes_text:
                    line.notes = notes_text
                line.save(update_fields=["counted_quantity", "counted_by", "unit_cost", "notes", "updated_at"])

        stock_count.updated_at = now
        stock_count.save(update_fields=["updated_at"])

        logger.info("Recorded %d count lines for stock count %s", len(lines_data), stock_count.count_number)
        return stock_count


    @transaction.atomic
    def submit_stock_count(self, tenant: Any, stock_count: StockCount, user: Any | None = None) -> StockCount:
        """Submit physical count data for review and variance computation."""
        if stock_count.count_status != CountStatus.IN_PROGRESS:
            raise InvalidCountStateError(f"Cannot submit stock count in status {stock_count.count_status}.")

        now = timezone.now()
        lines = stock_count.lines.all()

        total_counted = 0
        total_shortage = Decimal("0.00")
        total_overage = Decimal("0.00")
        total_cost_var = Decimal("0.0000")

        for line in lines:
            line.recalculate_variance()
            line.save(update_fields=["variance_quantity", "variance_percentage", "variance_cost", "variance_direction"])

            if line.counted_quantity is not None:
                total_counted += 1
                if line.variance_direction == VarianceDirection.SHORTAGE:
                    total_shortage += abs(line.variance_quantity)
                elif line.variance_direction == VarianceDirection.OVERAGE:
                    total_overage += line.variance_quantity
                total_cost_var += abs(line.variance_cost)

        stock_count.count_status = CountStatus.SUBMITTED
        stock_count.submitted_at = now
        stock_count.completed_by = user
        stock_count.total_items_counted = total_counted
        stock_count.total_shortage_quantity = total_shortage
        stock_count.total_overage_quantity = total_overage
        stock_count.total_variance_cost = total_cost_var
        stock_count.save()

        self._record_history(tenant, stock_count, "SUBMITTED", user, {
            "total_items_counted": total_counted,
            "total_variance_cost": str(total_cost_var),
        })
        logger.info("Submitted stock count %s", stock_count.count_number)
        return stock_count

    @transaction.atomic
    def request_recount(
        self,
        tenant: Any,
        stock_count: StockCount,
        line_ids: list[str],
        reason: str,
        user: Any | None = None,
    ) -> StockCount:
        """Flag specific count lines for recount and advance status to RECOUNT_REQUIRED."""
        if stock_count.count_status not in [CountStatus.SUBMITTED, CountStatus.UNDER_REVIEW]:
            raise InvalidCountStateError(f"Cannot request recount for stock count in status {stock_count.count_status}.")

        lines = stock_count.lines.filter(pk__in=line_ids)
        for line in lines:
            recount_num = self.number_generator.generate_recount_number(tenant)
            self.recount_repository.create(
                tenant=tenant,
                stock_count=stock_count,
                stock_count_line=line,
                recount_number=recount_num,
                requested_by=user,
                original_counted_quantity=line.counted_quantity or Decimal("0.00"),
                reason=reason,
                recount_status=RecountStatus.REQUESTED,
            )
            line.requires_recount = True
            line.recount_reason = reason
            line.save(update_fields=["requires_recount", "recount_reason", "updated_at"])

        stock_count.count_status = CountStatus.RECOUNT_REQUIRED
        stock_count.save(update_fields=["count_status", "updated_at"])

        self._record_history(tenant, stock_count, "RECOUNT_REQUESTED", user, {"recount_lines_count": lines.count(), "reason": reason})
        logger.info("Requested recount for %d lines in stock count %s", lines.count(), stock_count.count_number)
        return stock_count

    @transaction.atomic
    def approve_stock_count(self, tenant: Any, stock_count: StockCount, user: Any | None = None) -> StockCount:
        """Approve calculated stock count variances after separation of duties and threshold verification."""
        if stock_count.count_status not in [CountStatus.SUBMITTED, CountStatus.UNDER_REVIEW, CountStatus.PENDING_APPROVAL]:
            raise InvalidCountStateError(f"Cannot approve stock count in status {stock_count.count_status}.")

        # Separation of duties check: Counter user cannot approve their own high-variance count
        if stock_count.completed_by and user and not getattr(user, "is_superuser", False):
            if stock_count.completed_by.id == user.id and stock_count.total_variance_cost > Decimal("0.0000"):
                validate_user_not_same_as_counter(stock_count.completed_by, user, is_superuser=False)

        now = timezone.now()
        stock_count.count_status = CountStatus.APPROVED
        stock_count.approved_at = now
        stock_count.approved_by = user
        stock_count.save(update_fields=["count_status", "approved_at", "approved_by", "updated_at"])

        self._record_history(tenant, stock_count, "APPROVED", user, {"approved_by": str(user)})
        logger.info("Approved stock count %s", stock_count.count_number)
        return stock_count

    @transaction.atomic
    def reconcile_stock_count(
        self,
        tenant: Any,
        stock_count: StockCount,
        user: Any | None = None,
        idempotency_key: str = "",
    ) -> StockCount:
        """Execute physical stock position adjustments through StockMovementEngine cleanly and idempotently."""
        stock_count = (
            StockCount.objects.filter(tenant=tenant, pk=stock_count.pk)
            .select_for_update()
            .first()
        )
        if not stock_count:
            raise InvalidCountStateError("Stock count does not exist.")

        if stock_count.count_status == CountStatus.RECONCILED:
            logger.info("Stock count %s is already reconciled. Returning existing document idempotently.", stock_count.count_number)
            return stock_count

        if stock_count.count_status not in [CountStatus.APPROVED, CountStatus.SUBMITTED]:
            raise InvalidCountStateError(f"Cannot reconcile stock count in status {stock_count.count_status}. Must be APPROVED.")

        now = timezone.now()
        lines = list(stock_count.lines.filter(counted_quantity__isnull=False))

        for line in lines:
            line.recalculate_variance()
            line.save(update_fields=["variance_quantity", "variance_cost", "variance_direction"])

            if line.variance_quantity == Decimal("0.00"):
                continue

            # Fetch live inventory item position safely with row lock
            item = InventoryItem.objects.filter(
                tenant=tenant,
                warehouse=stock_count.warehouse,
                storage_location=line.storage_location,
                medicine=line.medicine,
                batch=line.batch,
            ).select_for_update().first()

            # Calculate true effective adjustment needed against current live inventory
            current_live_qty = item.on_hand_quantity if item else Decimal("0.00")
            effective_adjustment = Decimal(str(line.counted_quantity)) - current_live_qty

            if effective_adjustment == Decimal("0.00"):
                continue

            if effective_adjustment > Decimal("0.00"):
                # Overage -> ADJUSTMENT_IN
                self.movement_engine.create_movement(
                    tenant=tenant,
                    company=stock_count.company,
                    branch=stock_count.branch,
                    warehouse=stock_count.warehouse,
                    destination_location=line.storage_location,
                    medicine=line.medicine,
                    batch=line.batch,
                    movement_type=MovementType.ADJUSTMENT_IN,
                    quantity=effective_adjustment,
                    unit_cost=line.unit_cost,
                    reference_type=ReferenceType.OTHER,
                    reference_id=str(stock_count.pk),
                    reference_number=stock_count.count_number,
                    reason=f"Stock count overage reconciliation for {stock_count.count_number}",
                    performed_by=user,
                    auto_process=True,
                )
            else:
                # Shortage -> ADJUSTMENT_OUT
                self.movement_engine.create_movement(
                    tenant=tenant,
                    company=stock_count.company,
                    branch=stock_count.branch,
                    warehouse=stock_count.warehouse,
                    source_location=line.storage_location,
                    medicine=line.medicine,
                    batch=line.batch,
                    movement_type=MovementType.ADJUSTMENT_OUT,
                    quantity=abs(effective_adjustment),
                    unit_cost=line.unit_cost,
                    reference_type=ReferenceType.OTHER,
                    reference_id=str(stock_count.pk),
                    reference_number=stock_count.count_number,
                    reason=f"Stock count shortage reconciliation for {stock_count.count_number}",
                    performed_by=user,
                    auto_process=True,
                )


        stock_count.count_status = CountStatus.RECONCILED
        stock_count.reconciled_at = now
        stock_count.reconciled_by = user
        stock_count.save(update_fields=["count_status", "reconciled_at", "reconciled_by", "updated_at"])

        self._record_history(tenant, stock_count, "RECONCILED", user, {"reconciled_by": str(user)})
        logger.info("Reconciled stock count %s through StockMovementEngine", stock_count.count_number)
        return stock_count

    @transaction.atomic
    def cancel_stock_count(self, tenant: Any, stock_count: StockCount, user: Any | None = None) -> StockCount:
        """Cancel an un-reconciled stock count."""
        if stock_count.count_status == CountStatus.RECONCILED:
            raise InvalidCountStateError("Cannot cancel an already reconciled stock count.")
        if stock_count.count_status == CountStatus.CANCELLED:
            raise CountAlreadyCancelledError("Stock count has already been cancelled.")

        stock_count.count_status = CountStatus.CANCELLED
        stock_count.cancelled_at = timezone.now()
        stock_count.save(update_fields=["count_status", "cancelled_at", "updated_at"])

        self._record_history(tenant, stock_count, "CANCELLED", user, {"cancelled_by": str(user)})
        logger.info("Cancelled stock count %s", stock_count.count_number)
        return stock_count

    def _record_history(self, tenant: Any, stock_count: StockCount, event_type: str, user: Any | None, details: dict[str, Any]) -> None:
        StockCountHistory.objects.create(
            tenant=tenant,
            stock_count=stock_count,
            event_type=event_type,
            performed_by=user,
            details=details,
        )
