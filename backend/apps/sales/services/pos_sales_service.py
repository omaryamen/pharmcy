"""Authoritative POS Sales domain service integrating FEFO, Stock Movement Engine, Cash Registers, and Customer Credit."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.inventory.repositories import InventoryItemRepository
from apps.sales.exceptions import (
    CashierSessionRequiredError,
    InsufficientStockForSaleError,
    InvalidSaleStateError,
)
from apps.sales.models import (
    CashRegister,
    InvoicePaymentStatus,
    RegisterSession,
    SalesInvoice,
    SalesInvoiceLine,
    SalesPayment,
    SalesPaymentMethod,
    SalesPaymentStatus,
    SalesStatus,
    SessionStatus,
)
from apps.sales.repositories import (
    CashRegisterRepository,
    RegisterSessionRepository,
    SalesInvoiceRepository,
    SalesPaymentRepository,
)
from apps.sales.services.fefo_selector import FEFOBatchSelector
from apps.sales.services.number_generator import SalesNumberGenerator
from apps.sales.validators import (
    calculate_cash_change,
    validate_batch_eligibility_for_sale,
    validate_customer_credit_sale,
)
from apps.stock_movement.models import MovementType, ReferenceType
from apps.stock_movement.services import StockMovementEngine

logger = logging.getLogger(__name__)


class PosSalesService:
    """Core domain service executing atomic POS retail sales, StockMovementEngine inventory reduction, mixed payments, and cash register sessions."""

    def __init__(self):
        self.repository = SalesInvoiceRepository()
        self.payment_repository = SalesPaymentRepository()
        self.register_repository = CashRegisterRepository()
        self.session_repository = RegisterSessionRepository()
        self.number_generator = SalesNumberGenerator()
        self.fefo_selector = FEFOBatchSelector()
        self.inventory_item_repository = InventoryItemRepository()
        self.movement_engine = StockMovementEngine()

    @transaction.atomic
    def create_draft_or_held_sale(
        self,
        tenant: Any,
        company: Any,
        branch: Any,
        warehouse: Any,
        lines_data: list[dict[str, Any]],
        *,
        customer: Any | None = None,
        register_session: Any | None = None,
        status: str = SalesStatus.DRAFT,
        currency: str = "USD",
        exchange_rate: Decimal | float | str = "1.000000",
        discount: Decimal | float | str = "0.0000",
        tax: Decimal | float | str = "0.0000",
        other_charges: Decimal | float | str = "0.0000",
        notes: str = "",
        idempotency_key: str = "",
        cashier: Any | None = None,
        salesperson: Any | None = None,
    ) -> SalesInvoice:
        """Create a SalesInvoice in DRAFT or HELD status without deducting inventory stock balance."""
        if idempotency_key:
            existing = self.repository.find_by_idempotency_key(tenant, idempotency_key)
            if existing:
                logger.info("Found existing SalesInvoice %s for idempotency_key %s", existing.invoice_number, idempotency_key)
                return existing

        now = timezone.now()
        inv_num = self.number_generator.generate_invoice_number(tenant)

        invoice = self.repository.create(
            tenant=tenant,
            company=company,
            branch=branch,
            warehouse=warehouse,
            customer=customer,
            register_session=register_session,
            invoice_number=inv_num,
            invoice_date=now.date(),
            invoice_time=now.time(),
            status=status,
            payment_status=InvoicePaymentStatus.UNPAID,
            currency=currency,
            exchange_rate=Decimal(str(exchange_rate)),
            discount=Decimal(str(discount)),
            tax=Decimal(str(tax)),
            other_charges=Decimal(str(other_charges)),
            idempotency_key=idempotency_key,
            cashier=cashier,
            salesperson=salesperson,
            notes=notes,
        )

        subtotal = Decimal("0.0000")

        for line_data in lines_data:
            med = line_data["medicine"]
            loc = line_data.get("storage_location") or warehouse.storage_locations.first()
            qty = Decimal(str(line_data["quantity"]))

            # Auto FEFO batch selection if batch not explicitly passed
            batch = line_data.get("batch")
            if not batch:
                batch, _ = self.fefo_selector.select_fefo_batch_for_sale(
                    tenant=tenant,
                    warehouse=warehouse,
                    storage_location=loc,
                    medicine=med,
                    required_quantity=qty,
                )

            validate_batch_eligibility_for_sale(batch)

            u_price = Decimal(str(line_data.get("unit_price", str(batch.selling_price))))
            disc_amt = Decimal(str(line_data.get("discount_amount", "0.0000")))
            tx_amt = Decimal(str(line_data.get("tax_amount", "0.0000")))

            line = SalesInvoiceLine.objects.create(
                tenant=tenant,
                sales_invoice=invoice,
                medicine=med,
                batch=batch,
                warehouse=warehouse,
                storage_location=loc,
                quantity=qty,
                unit=line_data.get("unit", "Pcs"),
                unit_price=u_price,
                discount_amount=disc_amt,
                tax_amount=tx_amt,
                cost_price=batch.unit_cost,
                notes=line_data.get("notes", ""),
            )
            line.calculate_line_financials()
            line.save()

            subtotal += line.line_subtotal

        invoice.subtotal = subtotal
        invoice.grand_total = (subtotal - invoice.discount) + invoice.tax + invoice.other_charges
        invoice.outstanding_amount = invoice.grand_total
        invoice.save(update_fields=["subtotal", "grand_total", "outstanding_amount", "updated_at"])

        logger.info("Created SalesInvoice %s (Status: %s)", inv_num, status)
        return invoice

    @transaction.atomic
    def complete_sale(
        self,
        tenant: Any,
        invoice: SalesInvoice,
        payments_data: list[dict[str, Any]],
        *,
        user: Any | None = None,
    ) -> SalesInvoice:
        """AUTHORITATIVE POS SALE ENGINE: Validates stock, executes physical stock reduction strictly via StockMovementEngine, processes payments, and completes sale."""
        invoice = (
            SalesInvoice.objects.filter(tenant=tenant, pk=invoice.pk)
            .select_for_update()
            .first()
        )
        if not invoice:
            raise InvalidSaleStateError("Sales invoice does not exist.")

        if invoice.status in [SalesStatus.COMPLETED, SalesStatus.PAID, SalesStatus.CREDIT]:
            logger.info("SalesInvoice %s is already completed. Returning existing object.", invoice.invoice_number)
            return invoice

        if invoice.status in [SalesStatus.CANCELLED, SalesStatus.VOIDED]:
            raise InvalidSaleStateError(f"Cannot complete sale in status {invoice.status}.")

        lines = list(invoice.lines.select_related("medicine", "batch", "storage_location"))
        if not lines:
            raise InvalidSaleStateError("Cannot complete sale with zero items.")

        # 1. STOCK VALIDATION & BATCH ELIGIBILITY CHECK FOR ALL LINES
        for line in lines:
            validate_batch_eligibility_for_sale(line.batch)

            inv_item = self.inventory_item_repository.get_exact_stock_position(
                tenant=tenant,
                warehouse_id=invoice.warehouse.id,
                storage_location_id=line.storage_location.id,
                medicine_id=line.medicine.id,
                batch_id=line.batch.id,
            )
            avail_stock = inv_item.available_quantity if inv_item else Decimal("0.00")

            if line.quantity > avail_stock:
                raise InsufficientStockForSaleError(
                    f"Insufficient stock for {line.medicine.english_name} (Batch {line.batch.batch_number}). "
                    f"Requested: {line.quantity}, Available: {avail_stock}."
                )

        # 2. PROCESS PHYSICAL INVENTORY REDUCTION VIA STOCK MOVEMENT ENGINE
        for line in lines:
            self.movement_engine.create_movement(
                tenant=tenant,
                company=invoice.company,
                branch=invoice.branch,
                warehouse=invoice.warehouse,
                source_warehouse=invoice.warehouse,
                source_location=line.storage_location,
                movement_type=MovementType.SALE,
                medicine=line.medicine,
                batch=line.batch,
                quantity=line.quantity,
                unit_cost=line.cost_price,
                reference_type=ReferenceType.SALES_INVOICE,
                reference_id=str(invoice.pk),
                reference_number=invoice.invoice_number,
                reason=f"POS Counter Sale: {invoice.invoice_number}",
                idempotency_key=f"POS-SALE-{invoice.pk}-{line.pk}",
                performed_by=user or invoice.cashier,
                auto_process=True,
            )

        # 3. PROCESS PAYMENTS & CHANGE CALCULATION
        total_paid = Decimal("0.0000")
        total_change = Decimal("0.0000")
        credit_paid_amount = Decimal("0.0000")
        is_credit_sale = False

        for pmt_data in payments_data:
            pmt_method = pmt_data.get("payment_method", SalesPaymentMethod.CASH)
            pmt_amount = Decimal(str(pmt_data["amount"]))
            tendered = Decimal(str(pmt_data.get("tendered_amount", str(pmt_amount))))

            if pmt_method == SalesPaymentMethod.CUSTOMER_CREDIT:
                is_credit_sale = True
                credit_paid_amount += pmt_amount
                if not invoice.customer:
                    raise InvalidSaleStateError("Customer required for credit sales.")
                validate_customer_credit_sale(invoice.customer, pmt_amount)

            change = Decimal("0.0000")
            if pmt_method == SalesPaymentMethod.CASH and tendered > pmt_amount:
                change = calculate_cash_change(tendered, pmt_amount)

            pmt_num = self.number_generator.generate_payment_number(tenant)
            self.payment_repository.create(
                tenant=tenant,
                sales_invoice=invoice,
                payment_number=pmt_num,
                payment_method=pmt_method,
                amount=pmt_amount,
                tendered_amount=tendered,
                change_amount=change,
                currency=invoice.currency,
                reference_number=pmt_data.get("reference_number", ""),
                status=SalesPaymentStatus.POSTED,
                created_by=user or invoice.cashier,
            )

            total_paid += pmt_amount
            total_change += change

            # Register Session Cash Tracking
            if pmt_method == SalesPaymentMethod.CASH and invoice.register_session:
                sess = invoice.register_session
                sess.cash_sales += pmt_amount
                sess.save(update_fields=["cash_sales", "updated_at"])

        # 4. UPDATE CUSTOMER CREDIT BALANCE IF APPLICABLE
        outstanding = invoice.grand_total - total_paid
        if is_credit_sale and invoice.customer:
            cust = invoice.customer
            cust.current_balance += credit_paid_amount
            cust.save(update_fields=["current_balance", "updated_at"])

        now = timezone.now()
        invoice.paid_amount = total_paid
        invoice.change_amount = total_change
        invoice.outstanding_amount = max(Decimal("0.0000"), outstanding)

        if invoice.outstanding_amount == Decimal("0.0000"):
            invoice.status = SalesStatus.COMPLETED
            invoice.payment_status = InvoicePaymentStatus.PAID
        elif is_credit_sale:
            invoice.status = SalesStatus.CREDIT
            invoice.payment_status = InvoicePaymentStatus.CREDIT
        else:
            invoice.status = SalesStatus.PARTIALLY_PAID
            invoice.payment_status = InvoicePaymentStatus.PARTIALLY_PAID

        invoice.completed_at = now
        invoice.save(update_fields=["paid_amount", "change_amount", "outstanding_amount", "status", "payment_status", "completed_at", "updated_at"])

        logger.info("Successfully completed POS Sale %s and deducted stock via StockMovementEngine", invoice.invoice_number)
        return invoice

    @transaction.atomic
    def void_completed_sale(self, tenant: Any, invoice: SalesInvoice, reason: str = "", user: Any | None = None) -> SalesInvoice:
        """Void a completed sale, restoring physical inventory via compensating StockMovementEngine movements."""
        invoice = (
            SalesInvoice.objects.filter(tenant=tenant, pk=invoice.pk)
            .select_for_update()
            .first()
        )
        if not invoice:
            raise InvalidSaleStateError("Sales invoice does not exist.")

        if invoice.status not in [SalesStatus.COMPLETED, SalesStatus.PAID, SalesStatus.CREDIT, SalesStatus.PARTIALLY_PAID]:
            raise InvalidSaleStateError(f"Cannot void sale in status {invoice.status}.")

        # Create compensating SALE_RETURN movements via StockMovementEngine
        for line in invoice.lines.all():
            self.movement_engine.create_movement(
                tenant=tenant,
                company=invoice.company,
                branch=invoice.branch,
                warehouse=invoice.warehouse,
                destination_warehouse=invoice.warehouse,
                destination_location=line.storage_location,
                movement_type=MovementType.SALE_RETURN,
                medicine=line.medicine,
                batch=line.batch,
                quantity=line.quantity,
                unit_cost=line.cost_price,
                reference_type=ReferenceType.SALES_RETURN,
                reference_id=str(invoice.pk),
                reference_number=invoice.invoice_number,
                reason=f"POS Sale Void: {reason}",
                idempotency_key=f"POS-VOID-{invoice.pk}-{line.pk}",
                performed_by=user or invoice.cashier,
                auto_process=True,
            )

        # Restore customer credit balance if applicable
        if invoice.customer and invoice.outstanding_amount > Decimal("0.0000"):
            cust = invoice.customer
            cust.current_balance -= invoice.outstanding_amount
            cust.save(update_fields=["current_balance", "updated_at"])

        now = timezone.now()
        invoice.status = SalesStatus.VOIDED
        invoice.cancelled_at = now
        invoice.notes = f"{invoice.notes}\n[VOIDED]: {reason}".strip()
        invoice.save(update_fields=["status", "cancelled_at", "notes", "updated_at"])

        logger.info("Voided SalesInvoice %s", invoice.invoice_number)
        return invoice

    @transaction.atomic
    def open_register_session(self, tenant: Any, register: CashRegister, cashier: Any, opening_cash: Decimal | float | str = "0.0000") -> RegisterSession:
        """Open a cashier shift session on a CashRegister."""
        op_cash = Decimal(str(opening_cash))
        ses_num = self.number_generator.generate_session_number(tenant)

        session = self.session_repository.create(
            tenant=tenant,
            cash_register=register,
            cashier=cashier,
            session_number=ses_num,
            opening_cash=op_cash,
            status=SessionStatus.OPEN,
        )
        register.status = "open"
        register.current_balance = op_cash
        register.save(update_fields=["status", "current_balance", "updated_at"])

        logger.info("Opened RegisterSession %s for cashier %s", ses_num, cashier.get_full_name())
        return session

    @transaction.atomic
    def close_register_session(
        self, tenant: Any, session: RegisterSession, actual_cash: Decimal | float | str, notes: str = ""
    ) -> RegisterSession:
        """Close cashier shift session, calculate cash reconciliation variance."""
        session = (
            RegisterSession.objects.filter(tenant=tenant, pk=session.pk)
            .select_for_update()
            .first()
        )
        act_cash = Decimal(str(actual_cash))

        session.actual_cash = act_cash
        session.calculate_reconciliation()
        session.status = SessionStatus.CLOSED
        session.closed_at = timezone.now()
        session.notes = notes
        session.save()

        reg = session.cash_register
        reg.status = "closed"
        reg.current_balance = act_cash
        reg.save(update_fields=["status", "current_balance", "updated_at"])

        logger.info("Closed RegisterSession %s (Variance: %s)", session.session_number, session.variance)
        return session
