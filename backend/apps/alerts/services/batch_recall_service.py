"""Authoritative Batch Recall Service executing regulatory recall orders and automated stock quarantining."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.alerts.exceptions import InvalidRecallStateError, RecallAlreadyCompletedError, RecallAlreadyInitiatedError
from apps.alerts.models import AlertSeverity, AlertStatus, AlertType, BatchRecall, RecallClass, RecallStatus, RecallType
from apps.alerts.repositories import BatchRecallRepository
from apps.alerts.services.number_generator import AlertNumberGenerator
from apps.inventory.models import InventoryItem
from apps.stock_movement.models import MovementType, ReferenceType
from apps.stock_movement.services import StockMovementEngine

logger = logging.getLogger(__name__)


class BatchRecallService:
    """Orchestrates pharmaceutical batch recall operations and automated inventory quarantine via StockMovementEngine."""

    def __init__(self):
        self.recall_repository = BatchRecallRepository()
        self.number_generator = AlertNumberGenerator()
        self.movement_engine = StockMovementEngine()

    @transaction.atomic
    def create_recall(
        self,
        tenant: Any,
        company: Any,
        medicine: Any,
        batch: Any,
        reason: str,
        *,
        recall_type: str = RecallType.VOLUNTARY_MANUFACTURER,
        recall_class: str = RecallClass.CLASS_2_URGENT,
        action_required: str = "",
        regulatory_reference: str = "",
        user: Any | None = None,
    ) -> BatchRecall:
        """Create a new BatchRecall draft document."""
        recall_num = self.number_generator.generate_recall_number(tenant)

        recall = self.recall_repository.create(
            tenant=tenant,
            company=company,
            medicine=medicine,
            batch=batch,
            recall_number=recall_num,
            recall_type=recall_type,
            recall_class=recall_class,
            status=RecallStatus.DRAFT,
            reason=reason,
            action_required=action_required,
            regulatory_reference=regulatory_reference,
            initiated_by=user,
        )
        logger.info("Created batch recall %s for batch %s", recall_num, batch.batch_number)
        return recall

    @transaction.atomic
    def initiate_recall(
        self,
        tenant: Any,
        recall: BatchRecall,
        auto_quarantine: bool = True,
        user: Any | None = None,
    ) -> BatchRecall:
        """Initiate recall order, set batch status to 'recalled', generate recall alerts, and optionally quarantine stock."""
        if recall.status not in [RecallStatus.DRAFT]:
            raise RecallAlreadyInitiatedError()

        now = timezone.now()
        batch = recall.batch
        batch.status = "recalled"
        batch.save(update_fields=["status", "updated_at"])

        recall.status = RecallStatus.INITIATED
        recall.initiated_at = now
        recall.initiated_by = user or recall.initiated_by
        recall.save(update_fields=["status", "initiated_at", "initiated_by", "updated_at"])

        # Execute automated stock quarantining if requested
        if auto_quarantine:
            self.auto_quarantine_stock(tenant, recall, user=user)

        logger.info("Initiated batch recall %s for batch %s", recall.recall_number, batch.batch_number)
        return recall

    @transaction.atomic
    def auto_quarantine_stock(
        self,
        tenant: Any,
        recall: BatchRecall,
        user: Any | None = None,
    ) -> Decimal:
        """Find all active inventory items for recalled batch across all warehouses and execute QUARANTINE movements via StockMovementEngine."""
        batch = recall.batch
        items = InventoryItem.objects.filter(
            tenant=tenant,
            batch=batch,
            on_hand_quantity__gt=Decimal("0"),
        ).select_related("company", "warehouse", "storage_location", "medicine")

        total_quarantined = Decimal("0.0000")

        for item in items:
            if item.on_hand_quantity <= Decimal("0"):
                continue

            qty_to_quarantine = item.available_quantity
            if qty_to_quarantine <= Decimal("0"):
                continue

            # Execute QUARANTINE movement via StockMovementEngine
            self.movement_engine.create_movement(
                tenant=tenant,
                company=item.company,
                warehouse=item.warehouse,
                source_location=item.storage_location,
                medicine=item.medicine,
                batch=batch,
                movement_type=MovementType.QUARANTINE,
                quantity=qty_to_quarantine,
                unit_cost=item.unit_cost,
                reference_type=ReferenceType.OTHER,
                reference_id=str(recall.pk),
                reference_number=recall.recall_number,
                reason=f"Batch Recall Quarantine: {recall.recall_number}",
                performed_by=user,
                auto_process=True,
            )
            total_quarantined += qty_to_quarantine

        recall.quarantined_quantity += total_quarantined
        recall.status = RecallStatus.QUARANTINED
        recall.save(update_fields=["quarantined_quantity", "status", "updated_at"])

        logger.info("Auto-quarantined %s units for batch recall %s", total_quarantined, recall.recall_number)
        return total_quarantined

    @transaction.atomic
    def complete_recall(
        self,
        tenant: Any,
        recall: BatchRecall,
        disposed_quantity: Decimal = Decimal("0"),
        returned_quantity: Decimal = Decimal("0"),
        user: Any | None = None,
    ) -> BatchRecall:
        """Finalize and close batch recall order."""
        if recall.status in [RecallStatus.COMPLETED, RecallStatus.CANCELLED]:
            raise RecallAlreadyCompletedError()

        now = timezone.now()
        recall.disposed_quantity = disposed_quantity
        recall.returned_quantity = returned_quantity
        recall.status = RecallStatus.COMPLETED
        recall.completed_at = now
        recall.completed_by = user
        recall.save(update_fields=["disposed_quantity", "returned_quantity", "status", "completed_at", "completed_by", "updated_at"])

        logger.info("Completed batch recall %s", recall.recall_number)
        return recall
