"""OrderFulfillmentService executing FEFO inventory deduction and delivery dispatch."""

from __future__ import annotations

import logging
import uuid
from decimal import Decimal
from typing import Any
from django.db import transaction
from django.utils import timezone

from apps.commerce.exceptions import PrescriptionRequiredError, StockUnavailableError
from apps.commerce.models import (
    CommerceOrder,
    CommerceOrderStatus,
    OrderDelivery,
    PrescriptionReviewStatus,
)
from apps.notifications.services import EventPublisherService
from apps.inventory.models import InventoryItem
from apps.warehouses.models import StorageLocation
from apps.stock_movement.models.enums import MovementType
from apps.stock_movement.services import StockMovementEngine

logger = logging.getLogger(__name__)


class OrderFulfillmentService:
    """Service layer fulfilling orders, moving stock via StockMovementEngine, and managing dispatch."""

    def __init__(
        self,
        stock_engine: StockMovementEngine | None = None,
        event_publisher: EventPublisherService | None = None,
    ) -> None:
        self.stock_engine = stock_engine or StockMovementEngine()
        self.event_publisher = event_publisher or EventPublisherService()

    @transaction.atomic
    def fulfill_and_dispatch_order(
        self,
        order: CommerceOrder,
        *,
        courier_name: str = "PharmaExpress",
        tracking_number: str | None = None,
        user: Any | None = None,
    ) -> OrderDelivery:
        """Fulfill order items by deducting stock via StockMovementEngine and assigning delivery tracking."""
        # 1. Prescription check
        rx = order.prescriptions.first()
        if rx and rx.review_status != PrescriptionReviewStatus.APPROVED:
            raise PrescriptionRequiredError("Cannot fulfill order; prescription has not been approved by pharmacist.")

        if not order.warehouse:
            raise StockUnavailableError("Fulfillment warehouse is required on the order.")

        # 2. Reduce inventory stock via StockMovementEngine (SALE movement with FEFO batch selection)
        source_loc = StorageLocation.objects.filter(warehouse=order.warehouse, is_deleted=False).first()
        lines_payload = []
        for line in order.lines.select_related("medicine").all():
            inv_item = (
                InventoryItem.objects.filter(
                    tenant=order.tenant,
                    warehouse=order.warehouse,
                    medicine=line.medicine,
                    on_hand_quantity__gte=line.quantity,
                    is_deleted=False,
                )
                .order_by("batch__expiry_date")
                .first()
            )
            batch = inv_item.batch if inv_item else None
            loc = inv_item.storage_location if inv_item else source_loc

            lines_payload.append(
                {
                    "medicine": line.medicine,
                    "batch": batch,
                    "quantity": line.quantity,
                    "unit_cost": line.unit_price,
                    "source_location": loc,
                }
            )

        movement = self.stock_engine.create_movement(
            tenant=order.tenant,
            company=order.warehouse.company,
            warehouse=order.warehouse,
            movement_type=MovementType.SALE,
            source_warehouse=order.warehouse,
            source_location=source_loc,
            lines=lines_payload,
            reference_number=order.order_number,
            notes=f"E-Commerce fulfillment for {order.order_number}",
            performed_by=user,
            auto_process=True,
        )

        # 3. Create Order Delivery
        track_num = tracking_number or f"TRK-{uuid.uuid4().hex[:8].upper()}"
        delivery, _ = OrderDelivery.objects.get_or_create(
            tenant=order.tenant,
            order=order,
            defaults={
                "courier_name": courier_name,
                "tracking_number": track_num,
                "estimated_delivery": timezone.now() + timezone.timedelta(days=1),
            },
        )

        order.status = CommerceOrderStatus.OUT_FOR_DELIVERY
        order.save(update_fields=["status", "updated_at"])

        # 4. Publish Event
        self.event_publisher.publish_event(
            tenant=order.tenant,
            event_type="order.dispatched",
            source_module="commerce",
            source_object_id=str(order.pk),
            payload={
                "order_number": order.order_number,
                "tracking_number": delivery.tracking_number,
                "courier": courier_name,
            },
        )
        logger.info("Fulfilled and dispatched Order %s (Tracking: %s)", order.order_number, delivery.tracking_number)
        return delivery
