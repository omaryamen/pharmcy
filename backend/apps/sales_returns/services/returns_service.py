"""CustomerReturnService orchestrating return validation, inspection, stock restoration via StockMovementEngine, and refund processing."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.customers.models import Customer
from apps.sales.models import SalesInvoice, SalesInvoiceLine
from apps.sales_returns.exceptions import (
    ExceedsRefundableAmountError,
    InvalidReturnStateError,
    RefundAlreadyProcessedError,
)
from apps.sales_returns.models import (
    CustomerRefund,
    CustomerReturn,
    CustomerReturnLine,
    InspectionResult,
    ProductCondition,
    RefundMethod,
    RefundStatus,
    ReturnStatus,
)
from apps.sales_returns.repositories import CustomerRefundRepository, CustomerReturnRepository
from apps.sales_returns.services.number_generator import SalesReturnNumberGenerator
from apps.sales_returns.validators import (
    validate_return_approval_separation_of_duties,
    validate_returnable_quantity,
)
from apps.stock_movement.models.enums import MovementType, ReferenceType
from apps.stock_movement.services import StockMovementEngine

logger = logging.getLogger(__name__)


class CustomerReturnService:
    """Service layer executing customer returns, inspection, stock restoration, and refund disbursement."""

    def __init__(
        self,
        return_repository: CustomerReturnRepository | None = None,
        refund_repository: CustomerRefundRepository | None = None,
        number_generator: SalesReturnNumberGenerator | None = None,
        stock_movement_engine: StockMovementEngine | None = None,
    ) -> None:
        self.return_repository = return_repository or CustomerReturnRepository()
        self.refund_repository = refund_repository or CustomerRefundRepository()
        self.number_generator = number_generator or SalesReturnNumberGenerator()
        self.stock_movement_engine = stock_movement_engine or StockMovementEngine()

    @transaction.atomic
    def create_customer_return(
        self,
        tenant: Any,
        sales_invoice: SalesInvoice,
        lines_data: list[dict[str, Any]],
        return_reason: str,
        user: Any | None = None,
        customer: Customer | None = None,
        idempotency_key: str = "",
        notes: str = "",
    ) -> CustomerReturn:
        """Create a new CustomerReturn request against an existing SalesInvoice."""
        if idempotency_key:
            existing = self.return_repository.find_by_idempotency_key(tenant, idempotency_key)
            if existing:
                logger.info(f"Duplicate CustomerReturn request suppressed for key: {idempotency_key}")
                return existing

        ret_num = self.number_generator.generate_return_number(tenant)
        cust = customer or sales_invoice.customer

        customer_return = self.return_repository.create(
            tenant=tenant,
            company=sales_invoice.company,
            branch=sales_invoice.branch,
            warehouse=sales_invoice.warehouse,
            customer=cust,
            sales_invoice=sales_invoice,
            return_number=ret_num,
            return_date=timezone.now().date(),
            status=ReturnStatus.REQUESTED,
            return_reason=return_reason,
            currency=sales_invoice.currency,
            idempotency_key=idempotency_key,
            created_by=user,
            notes=notes,
        )

        subtotal = Decimal("0.0000")
        tax_total = Decimal("0.0000")
        discount_total = Decimal("0.0000")

        for item in lines_data:
            inv_line_id = item["sales_invoice_line_id"]
            req_qty = Decimal(str(item["requested_return_quantity"]))

            inv_line = SalesInvoiceLine.objects.select_for_update().get(pk=inv_line_id, tenant=tenant)

            returnable_qty = validate_returnable_quantity(
                requested_quantity=req_qty,
                original_sold_quantity=inv_line.quantity,
                previously_returned_quantity=inv_line.returned_quantity,
            )

            unit_price = inv_line.unit_price
            disc_portion = Decimal("0.0000")
            tax_portion = Decimal("0.0000")
            if inv_line.quantity > Decimal("0.0000"):
                disc_portion = (inv_line.discount_amount / inv_line.quantity) * req_qty
                tax_portion = (inv_line.tax_amount / inv_line.quantity) * req_qty

            line_total = (unit_price * req_qty) - disc_portion + tax_portion

            CustomerReturnLine.objects.create(
                tenant=tenant,
                customer_return=customer_return,
                sales_invoice_line=inv_line,
                medicine=inv_line.medicine,
                batch=inv_line.batch,
                warehouse=sales_invoice.warehouse,
                storage_location=inv_line.storage_location,
                original_sold_quantity=inv_line.quantity,
                previously_returned_quantity=inv_line.returned_quantity,
                returnable_quantity=returnable_qty,
                requested_return_quantity=req_qty,
                accepted_return_quantity=Decimal("0.0000"),
                rejected_return_quantity=Decimal("0.0000"),
                unit=inv_line.medicine.unit_of_measure or "Pcs",
                original_unit_price=unit_price,
                refund_unit_price=unit_price,
                discount_amount=disc_portion,
                tax_amount=tax_portion,
                refund_line_total=line_total,
                condition=item.get("condition", ProductCondition.SEALED),
                return_reason=item.get("return_reason", return_reason),
                notes=item.get("notes", ""),
            )

            subtotal += (unit_price * req_qty)
            discount_total += disc_portion
            tax_total += tax_portion

        customer_return.subtotal = subtotal
        customer_return.discount = discount_total
        customer_return.tax = tax_total
        customer_return.save(update_fields=["subtotal", "discount", "tax", "updated_at"])

        logger.info(f"Created CustomerReturn {ret_num} for invoice {sales_invoice.invoice_number}")
        return customer_return

    @transaction.atomic
    def approve_customer_return(self, tenant: Any, customer_return: CustomerReturn, user: Any) -> CustomerReturn:
        """Approve a requested customer return document enforcing separation of duties."""
        ret = CustomerReturn.objects.select_for_update().get(pk=customer_return.pk, tenant=tenant)
        if ret.status not in [ReturnStatus.REQUESTED, ReturnStatus.DRAFT, ReturnStatus.PENDING_APPROVAL]:
            raise InvalidReturnStateError(f"Cannot approve return in status '{ret.status}'.")

        validate_return_approval_separation_of_duties(ret.created_by, user)

        ret.status = ReturnStatus.APPROVED
        ret.approved_by = user
        ret.approved_at = timezone.now()
        ret.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])

        logger.info(f"Approved CustomerReturn {ret.return_number} by {user}")
        return ret

    @transaction.atomic
    def inspect_and_accept_return(
        self,
        tenant: Any,
        customer_return: CustomerReturn,
        inspection_data: list[dict[str, Any]],
        inspector: Any,
    ) -> CustomerReturn:
        """Inspect return items, log accepted/rejected quantities, and restore stock strictly via StockMovementEngine."""
        ret = CustomerReturn.objects.select_for_update().get(pk=customer_return.pk, tenant=tenant)
        if ret.status not in [ReturnStatus.APPROVED, ReturnStatus.INSPECTION, ReturnStatus.REQUESTED]:
            raise InvalidReturnStateError(f"Cannot inspect return in status '{ret.status}'.")

        total_accepted_value = Decimal("0.0000")
        total_accepted_qty = Decimal("0.0000")
        total_rejected_qty = Decimal("0.0000")

        for item_data in inspection_data:
            line_id = item_data["line_id"]
            line = CustomerReturnLine.objects.select_for_update().get(pk=line_id, customer_return=ret, tenant=tenant)

            acc_qty = Decimal(str(item_data["accepted_quantity"]))
            rej_qty = Decimal(str(item_data.get("rejected_quantity", "0.0000")))
            cond = item_data.get("condition", line.condition)
            insp_res = item_data.get("inspection_result", InspectionResult.ACCEPTED)

            if (acc_qty + rej_qty) > line.requested_return_quantity:
                raise ExceedsReturnableQuantityError("Accepted + Rejected quantity exceeds requested return quantity.")

            line.accepted_return_quantity = acc_qty
            line.rejected_return_quantity = rej_qty
            line.condition = cond
            line.inspection_result = insp_res
            line.calculate_line_refund()
            line.save()

            total_accepted_value += line.refund_line_total
            total_accepted_qty += acc_qty
            total_rejected_qty += rej_qty

            # RESTORE INVENTORY STRICTLY VIA STOCK MOVEMENT ENGINE
            if acc_qty > Decimal("0.0000"):
                m_type = MovementType.SALE_RETURN
                if cond in [
                    ProductCondition.DAMAGED,
                    ProductCondition.OPENED,
                    ProductCondition.QUARANTINED,
                    ProductCondition.RECALLED,
                    ProductCondition.TEMPERATURE_DAMAGED,
                ] or insp_res in [InspectionResult.QUARANTINED, InspectionResult.DAMAGED]:
                    m_type = MovementType.QUARANTINE

                self.stock_movement_engine.create_movement(
                    tenant=tenant,
                    company=ret.company,
                    branch=ret.branch,
                    warehouse=ret.warehouse,
                    source_warehouse=ret.warehouse,
                    source_location=line.storage_location,
                    destination_warehouse=ret.warehouse,
                    destination_location=line.storage_location,
                    movement_type=m_type,
                    medicine=line.medicine,
                    batch=line.batch,
                    quantity=acc_qty,
                    unit_cost=line.batch.unit_cost,
                    reference_type=ReferenceType.SALES_RETURN,
                    reference_id=str(ret.pk),
                    reference_number=ret.return_number,
                    reason=f"Customer Return Inspection: {insp_res} ({cond})",
                    idempotency_key=f"CRT-STOCK-{ret.pk}-{line.pk}",
                    performed_by=inspector,
                    auto_process=True,
                )

                # Update original SalesInvoiceLine returned_quantity
                inv_line = line.sales_invoice_line
                inv_line.returned_quantity += acc_qty
                inv_line.save(update_fields=["returned_quantity", "updated_at"])

        ret.refund_amount = total_accepted_value
        ret.inspected_by = inspector

        if total_accepted_qty > Decimal("0.0000") and total_rejected_qty > Decimal("0.0000"):
            ret.status = ReturnStatus.PARTIALLY_ACCEPTED
        elif total_accepted_qty > Decimal("0.0000"):
            ret.status = ReturnStatus.ACCEPTED
        else:
            ret.status = ReturnStatus.REJECTED

        ret.save(update_fields=["refund_amount", "inspected_by", "status", "updated_at"])

        logger.info(f"Inspected CustomerReturn {ret.return_number}: Status {ret.status}, Eligible Refund ${total_accepted_value}")
        return ret

    @transaction.atomic
    def process_customer_refund(
        self,
        tenant: Any,
        customer_return: CustomerReturn,
        refund_method: str,
        amount: Decimal | float | int,
        user: Any,
        reference_number: str = "",
        notes: str = "",
    ) -> CustomerRefund:
        """Disburse customer refund or issue customer store credit for accepted return."""
        ret = CustomerReturn.objects.select_for_update().get(pk=customer_return.pk, tenant=tenant)
        if ret.refunds.filter(status=RefundStatus.COMPLETED).exists() or ret.status in [ReturnStatus.REFUNDED, ReturnStatus.STORE_CREDIT_ISSUED]:
            raise RefundAlreadyProcessedError("A refund has already been completed for this customer return.")

        if ret.status not in [ReturnStatus.ACCEPTED, ReturnStatus.PARTIALLY_ACCEPTED, ReturnStatus.REFUND_PENDING]:
            raise InvalidReturnStateError(f"Cannot process refund for return in status '{ret.status}'.")

        ref_amount = Decimal(str(amount))
        if ref_amount > ret.refund_amount:
            raise ExceedsRefundableAmountError(f"Refund amount ${ref_amount} exceeds eligible return refund value ${ret.refund_amount}.")

        ref_num = self.number_generator.generate_refund_number(tenant)
        refund = self.refund_repository.create(
            tenant=tenant,
            customer_return=ret,
            customer=ret.customer,
            sales_invoice=ret.sales_invoice,
            refund_number=ref_num,
            refund_method=refund_method,
            amount=ref_amount,
            currency=ret.currency,
            reference_number=reference_number,
            status=RefundStatus.COMPLETED,
            created_by=user,
            processed_by=user,
            processed_at=timezone.now(),
            notes=notes,
        )

        if refund_method == RefundMethod.STORE_CREDIT:
            ret.store_credit_amount = ref_amount
            ret.status = ReturnStatus.STORE_CREDIT_ISSUED
            if ret.customer:
                cust = ret.customer
                cust.current_balance -= ref_amount  # Reduces customer credit liability / balance
                cust.save(update_fields=["current_balance", "updated_at"])
        else:
            ret.status = ReturnStatus.REFUNDED

        ret.completed_at = timezone.now()
        ret.processed_by = user
        ret.save(update_fields=["store_credit_amount", "status", "completed_at", "processed_by", "updated_at"])

        logger.info(f"Processed CustomerRefund {ref_num} (${ref_amount} via {refund_method}) for return {ret.return_number}")
        return refund

    @transaction.atomic
    def reverse_customer_return(self, tenant: Any, customer_return: CustomerReturn, user: Any, reason: str = "") -> CustomerReturn:
        """Reverse a completed customer return, creating compensating stock movements and reversing customer balances."""
        ret = CustomerReturn.objects.select_for_update().get(pk=customer_return.pk, tenant=tenant)
        if ret.status not in [ReturnStatus.ACCEPTED, ReturnStatus.PARTIALLY_ACCEPTED, ReturnStatus.REFUNDED, ReturnStatus.STORE_CREDIT_ISSUED]:
            raise InvalidReturnStateError(f"Cannot reverse return in status '{ret.status}'.")

        # Reverse stock movements for accepted lines
        for line in ret.lines.filter(accepted_return_quantity__gt=Decimal("0.0000")):
            self.stock_movement_engine.create_movement(
                tenant=tenant,
                company=ret.company,
                branch=ret.branch,
                warehouse=ret.warehouse,
                source_warehouse=ret.warehouse,
                source_location=line.storage_location,
                movement_type=MovementType.SALE,
                medicine=line.medicine,
                batch=line.batch,
                quantity=line.accepted_return_quantity,
                unit_cost=line.batch.unit_cost,
                reference_type=ReferenceType.SALES_RETURN,
                reference_id=str(ret.pk),
                reference_number=ret.return_number,
                reason=f"Customer Return Reversal: {reason}",
                idempotency_key=f"CRT-REVERSE-{ret.pk}-{line.pk}",
                performed_by=user,
                auto_process=True,
            )

            inv_line = line.sales_invoice_line
            inv_line.returned_quantity -= line.accepted_return_quantity
            inv_line.save(update_fields=["returned_quantity", "updated_at"])

        # Reverse Store Credit if issued
        if ret.store_credit_amount > Decimal("0.0000") and ret.customer:
            cust = ret.customer
            cust.current_balance += ret.store_credit_amount
            cust.save(update_fields=["current_balance", "updated_at"])

        ret.status = ReturnStatus.REVERSED
        ret.save(update_fields=["status", "updated_at"])

        logger.info(f"Reversed CustomerReturn {ret.return_number} by {user}")
        return ret
