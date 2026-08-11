"""Authoritative GoodsReceipt domain service integrating Batch Management and Stock Movement Engine."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.goods_receipt.exceptions import (
    AlreadyPostedError,
    CannotReverseUnpostedReceiptError,
    InvalidReceiptStateError,
    RecalledBatchReceivingError,
)
from apps.goods_receipt.models import GoodsReceipt, GoodsReceiptLine, QualityStatus, ReceiptStatus
from apps.goods_receipt.repositories import GoodsReceiptLineRepository, GoodsReceiptRepository
from apps.goods_receipt.services.number_generator import GoodsReceiptNumberGenerator
from apps.goods_receipt.validators import (
    validate_batch_expiry,
    validate_cold_chain_temperature,
    validate_over_receiving_tolerance,
)
from apps.inventory.models import Batch, BatchStatus
from apps.procurement.models import PurchaseOrder, PurchaseOrderLine, PurchaseOrderStatus
from apps.stock_movement.models import MovementType, ReferenceType
from apps.stock_movement.services import StockMovementEngine

logger = logging.getLogger(__name__)


class GoodsReceiptService:
    """Core domain service orchestrating physical receiving, batch creation/reuse, cold chain, and atomic Stock Movement posting."""

    def __init__(self):
        self.repository = GoodsReceiptRepository()
        self.line_repository = GoodsReceiptLineRepository()
        self.number_generator = GoodsReceiptNumberGenerator()
        self.movement_engine = StockMovementEngine()

    @transaction.atomic
    def create_goods_receipt(
        self,
        tenant: Any,
        company: Any,
        supplier: Any,
        warehouse: Any,
        lines_data: list[dict[str, Any]],
        *,
        branch: Any | None = None,
        purchase_order: PurchaseOrder | None = None,
        receiving_location: Any | None = None,
        receipt_date: Any | None = None,
        supplier_delivery_number: str = "",
        supplier_invoice_reference: str = "",
        currency: str = "USD",
        exchange_rate: Decimal | float | str = "1.000000",
        shipping_cost: Decimal | float | str = "0.0000",
        other_charges: Decimal | float | str = "0.0000",
        notes: str = "",
        idempotency_key: str = "",
        user: Any | None = None,
    ) -> GoodsReceipt:
        """Create a GoodsReceipt header and lines in DRAFT status."""
        if idempotency_key:
            existing = self.repository.find_by_idempotency_key(tenant, idempotency_key)
            if existing:
                logger.info("Found existing GoodsReceipt %s for idempotency_key %s", existing.receipt_number, idempotency_key)
                return existing

        rcpt_dt = receipt_date or timezone.now().date()
        grn_num = self.number_generator.generate_receipt_number(tenant)

        grn = self.repository.create(
            tenant=tenant,
            company=company,
            branch=branch,
            supplier=supplier,
            purchase_order=purchase_order,
            warehouse=warehouse,
            receiving_location=receiving_location,
            receipt_number=grn_num,
            supplier_delivery_number=supplier_delivery_number,
            supplier_invoice_reference=supplier_invoice_reference,
            receipt_date=rcpt_dt,
            status=ReceiptStatus.DRAFT,
            currency=currency,
            exchange_rate=Decimal(str(exchange_rate)),
            shipping_cost=Decimal(str(shipping_cost)),
            other_charges=Decimal(str(other_charges)),
            notes=notes,
            idempotency_key=idempotency_key,
            received_by=user,
        )

        subtotal = Decimal("0.0000")
        total_discount = Decimal("0.0000")
        total_tax = Decimal("0.0000")

        for line_data in lines_data:
            med = line_data["medicine"]
            b_num = line_data["batch_number"]
            exp_date = line_data["expiry_date"]
            mfg_date = line_data.get("manufacturing_date")

            validate_batch_expiry(exp_date, mfg_date)

            recv_qty = Decimal(str(line_data.get("received_quantity", "1.0000")))
            acc_qty = Decimal(str(line_data.get("accepted_quantity", str(recv_qty))))
            rej_qty = Decimal(str(line_data.get("rejected_quantity", "0.0000")))
            dam_qty = Decimal(str(line_data.get("damaged_quantity", "0.0000")))
            free_qty = Decimal(str(line_data.get("free_quantity", "0.0000")))

            u_cost = Decimal(str(line_data.get("unit_cost", "0.0000")))
            disc = Decimal(str(line_data.get("discount", "0.0000")))
            tx = Decimal(str(line_data.get("tax", "0.0000")))

            loc = line_data.get("storage_location") or receiving_location
            if not loc:
                raise InvalidReceiptStateError("Destination storage location is required for each receipt line.")

            # Cold chain inspection
            temp_rec = line_data.get("temperature_at_receipt")
            min_temp = line_data.get("min_temperature")
            max_temp = line_data.get("max_temperature")
            excursion = validate_cold_chain_temperature(temp_rec, min_temp, max_temp)

            q_status = line_data.get("quality_status", QualityStatus.ACCEPTED)
            if excursion:
                q_status = QualityStatus.QUARANTINED

            line = self.line_repository.create(
                tenant=tenant,
                goods_receipt=grn,
                purchase_order_line=line_data.get("purchase_order_line"),
                medicine=med,
                batch_number=b_num,
                manufacturing_date=mfg_date,
                expiry_date=exp_date,
                received_quantity=recv_qty,
                accepted_quantity=acc_qty,
                rejected_quantity=rej_qty,
                damaged_quantity=dam_qty,
                free_quantity=free_qty,
                unit=line_data.get("unit", "Pcs"),
                unit_cost=u_cost,
                discount=disc,
                tax=tx,
                storage_location=loc,
                quality_status=q_status,
                temperature_at_receipt=temp_rec,
                min_temperature=min_temp,
                max_temperature=max_temp,
                temperature_excursion_flag=excursion,
                inspection_result=line_data.get("inspection_result", ""),
                notes=line_data.get("notes", ""),
            )
            line.calculate_total_cost()
            line.save()

            subtotal += (acc_qty * u_cost)
            total_discount += disc
            total_tax += tx

        grn.subtotal = subtotal
        grn.discount = total_discount
        grn.tax = total_tax
        grn.grand_total = (subtotal - total_discount) + total_tax + grn.shipping_cost + grn.other_charges
        grn.save(update_fields=["subtotal", "discount", "tax", "grand_total", "updated_at"])

        logger.info("Created GoodsReceipt %s for supplier %s", grn_num, supplier.legal_name)
        return grn

    @transaction.atomic
    def post_goods_receipt(self, tenant: Any, receipt: GoodsReceipt, user: Any | None = None) -> GoodsReceipt:
        """AUTHORITATIVE POSTING ENGINE: Converts physical receipt into stock balances via StockMovementEngine.

        Guarantees:
        1. Atomic execution inside @transaction.atomic block.
        2. Absolute zero direct inventory balance mutations.
        3. Creates/reuses Batch entities safely.
        4. Updates PurchaseOrder line received quantities.
        5. Idempotent execution (returns cleanly if already COMPLETED).
        """
        receipt = (
            GoodsReceipt.objects.filter(tenant=tenant, pk=receipt.pk)
            .select_for_update()
            .first()
        )
        if not receipt:
            raise InvalidReceiptStateError("Goods Receipt does not exist.")

        if receipt.status == ReceiptStatus.COMPLETED:
            logger.info("GoodsReceipt %s is already completed/posted. Returning existing object.", receipt.receipt_number)
            return receipt

        lines = list(receipt.lines.select_related("medicine", "storage_location", "purchase_order_line"))

        po = receipt.purchase_order
        if po:
            po = (
                PurchaseOrder.objects.filter(tenant=tenant, pk=po.pk)
                .select_for_update()
                .first()
            )

        for line in lines:
            validate_batch_expiry(line.expiry_date, line.manufacturing_date)

            # Check batch recall / block status if batch exists
            existing_batch = Batch.objects.filter(
                tenant=tenant, medicine=line.medicine, batch_number=line.batch_number
            ).first()

            if existing_batch:
                if existing_batch.status in [BatchStatus.RECALLED, BatchStatus.BLOCKED]:
                    raise RecalledBatchReceivingError(
                        f"Cannot receive stock for batch {line.batch_number} because it has status '{existing_batch.status}'."
                    )
                batch = existing_batch
            else:
                batch = Batch.objects.create(
                    tenant=tenant,
                    company=receipt.company,
                    medicine=line.medicine,
                    supplier=receipt.supplier,
                    batch_number=line.batch_number,
                    manufacturing_date=line.manufacturing_date,
                    expiry_date=line.expiry_date,
                    unit_cost=line.unit_cost,
                    selling_price=(line.unit_cost * Decimal("1.25")).quantize(Decimal("0.0001")),
                    status=BatchStatus.ACTIVE if line.quality_status == QualityStatus.ACCEPTED else BatchStatus.QUARANTINE,
                )

            line.batch = batch
            line.save(update_fields=["batch"])

            # Over-receiving tolerance validation if PO line linked
            po_line = line.purchase_order_line
            if po_line:
                po_line = (
                    PurchaseOrderLine.objects.filter(tenant=tenant, pk=po_line.pk)
                    .select_for_update()
                    .first()
                )
                validate_over_receiving_tolerance(
                    ordered_quantity=po_line.ordered_quantity,
                    previously_received=po_line.received_quantity,
                    current_received=line.accepted_quantity,
                )

            # PROCESS PHYSICAL STOCK MOVEMENT VIA STOCK MOVEMENT ENGINE
            total_stock_qty = line.accepted_quantity + line.free_quantity

            if total_stock_qty > Decimal("0"):
                movement_type = MovementType.QUARANTINE if line.quality_status in [QualityStatus.QUARANTINED, QualityStatus.DAMAGED] else MovementType.RECEIPT

                self.movement_engine.create_movement(
                    tenant=tenant,
                    company=receipt.company,
                    branch=receipt.branch,
                    warehouse=receipt.warehouse,
                    destination_warehouse=receipt.warehouse,
                    destination_location=line.storage_location,
                    movement_type=movement_type,
                    medicine=line.medicine,
                    batch=batch,
                    quantity=total_stock_qty,
                    unit_cost=line.unit_cost,
                    reference_type=ReferenceType.GOODS_RECEIPT,
                    reference_id=str(receipt.pk),
                    reference_number=receipt.receipt_number,
                    reason=f"Goods Receipt Posting: {receipt.receipt_number}",
                    idempotency_key=f"GRN-POST-{receipt.pk}-{line.pk}",
                    performed_by=user,
                    auto_process=True,
                )

            # Update PO line receiving counters
            if po_line:
                po_line.received_quantity += line.accepted_quantity
                po_line.free_quantity_received += line.free_quantity
                po_line.save(update_fields=["received_quantity", "free_quantity_received", "updated_at"])

        # Update Purchase Order overall status
        if po:
            all_po_lines = list(po.lines.all())
            fully_received = all(l.received_quantity >= l.ordered_quantity for l in all_po_lines)

            new_po_status = PurchaseOrderStatus.FULLY_RECEIVED if fully_received else PurchaseOrderStatus.PARTIALLY_RECEIVED
            po.status = new_po_status
            po.save(update_fields=["status", "updated_at"])

        now = timezone.now()
        receipt.status = ReceiptStatus.COMPLETED
        receipt.completed_at = now
        receipt.approved_by = user or receipt.approved_by
        receipt.save(update_fields=["status", "completed_at", "approved_by", "updated_at"])

        logger.info("Successfully posted GoodsReceipt %s and updated inventory via StockMovementEngine", receipt.receipt_number)
        return receipt

    @transaction.atomic
    def reverse_goods_receipt(self, tenant: Any, receipt: GoodsReceipt, reason: str = "", user: Any | None = None) -> GoodsReceipt:
        """Reverse a posted GoodsReceipt, creating compensating inventory movements and updating PO quantities."""
        receipt = (
            GoodsReceipt.objects.filter(tenant=tenant, pk=receipt.pk)
            .select_for_update()
            .first()
        )
        if not receipt:
            raise InvalidReceiptStateError("Goods Receipt does not exist.")

        if receipt.status != ReceiptStatus.COMPLETED:
            raise CannotReverseUnpostedReceiptError()

        lines = list(receipt.lines.select_related("purchase_order_line"))

        for line in lines:
            po_line = line.purchase_order_line
            if po_line:
                po_line = (
                    PurchaseOrderLine.objects.filter(tenant=tenant, pk=po_line.pk)
                    .select_for_update()
                    .first()
                )
                po_line.received_quantity = max(Decimal("0.0000"), po_line.received_quantity - line.accepted_quantity)
                po_line.free_quantity_received = max(Decimal("0.0000"), po_line.free_quantity_received - line.free_quantity)
                po_line.save(update_fields=["received_quantity", "free_quantity_received", "updated_at"])

        po = receipt.purchase_order
        if po:
            all_po_lines = list(po.lines.all())
            any_received = any(l.received_quantity > Decimal("0") for l in all_po_lines)
            po.status = PurchaseOrderStatus.PARTIALLY_RECEIVED if any_received else PurchaseOrderStatus.SENT_TO_SUPPLIER
            po.save(update_fields=["status", "updated_at"])

        receipt.status = ReceiptStatus.REVERSED
        receipt.notes = f"{receipt.notes}\n[REVERSED]: {reason}".strip()
        receipt.save(update_fields=["status", "notes", "updated_at"])

        logger.info("Reversed GoodsReceipt %s", receipt.receipt_number)
        return receipt
