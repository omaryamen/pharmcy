"""CustomerReceivableService managing creation, credit validation, return credits, and subledger maintenance."""

from __future__ import annotations

import logging
from datetime import timedelta
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.accounts_receivable.models import ARStatus, CustomerReceivable
from apps.accounts_receivable.repositories import CustomerReceivableRepository
from apps.accounts_receivable.services.number_generator import ARNumberGenerator
from apps.accounts_receivable.validators import validate_credit_limit
from apps.branches.models import Branch
from apps.companies.models import Company
from apps.customers.models import Customer
from apps.sales.models import SalesInvoice

logger = logging.getLogger(__name__)


class CustomerReceivableService:
    """Service layer managing CustomerReceivable creation from POS credit sales, return adjustments, and customer debt balances."""

    def __init__(
        self,
        repository: CustomerReceivableRepository | None = None,
        number_generator: ARNumberGenerator | None = None,
    ) -> None:
        self.repository = repository or CustomerReceivableRepository()
        self.number_generator = number_generator or ARNumberGenerator()

    @transaction.atomic
    def sync_receivable_from_sales_invoice(
        self,
        tenant: Any,
        sales_invoice: SalesInvoice,
        due_days: int = 30,
        idempotency_key: str = "",
        user: Any | None = None,
    ) -> CustomerReceivable:
        """Create or update authoritative AR subledger record for a completed POS sales invoice."""
        if not sales_invoice.customer:
            raise ValueError("SalesInvoice must have an assigned customer to generate a CustomerReceivable entry.")

        existing = self.repository.find_by_sales_invoice(tenant, str(sales_invoice.pk))
        if existing:
            logger.info(f"CustomerReceivable already exists for SalesInvoice {sales_invoice.invoice_number}")
            return existing

        customer = Customer.objects.select_for_update().get(pk=sales_invoice.customer.pk, tenant=tenant)

        original_amount = Decimal(str(sales_invoice.grand_total))
        paid_amount = Decimal(str(sales_invoice.paid_amount))
        outstanding_amount = Decimal(str(sales_invoice.outstanding_amount))

        # Check credit limit if there is an outstanding unpaid balance (credit sale)
        if outstanding_amount > Decimal("0.0000"):
            validate_credit_limit(customer, outstanding_amount)

        due_date = timezone.now().date() + timedelta(days=due_days)
        ar_num = self.number_generator.generate_receivable_number(tenant)

        receivable = self.repository.create(
            tenant=tenant,
            company=sales_invoice.company,
            branch=sales_invoice.branch,
            customer=customer,
            sales_invoice=sales_invoice,
            receivable_number=ar_num,
            original_amount=original_amount,
            paid_amount=paid_amount,
            credit_amount=Decimal("0.0000"),
            refund_amount=Decimal("0.0000"),
            adjusted_amount=Decimal("0.0000"),
            outstanding_amount=outstanding_amount,
            currency=sales_invoice.currency,
            exchange_rate=sales_invoice.exchange_rate,
            invoice_date=sales_invoice.completed_at.date() if sales_invoice.completed_at else timezone.now().date(),
            due_date=due_date,
            status=ARStatus.PAID if outstanding_amount <= Decimal("0.0000") else ARStatus.OPEN,
            idempotency_key=idempotency_key or f"AR-INV-{sales_invoice.pk}",
            created_by=user,
        )

        # Update customer debt balance
        if outstanding_amount > Decimal("0.0000"):
            customer.current_balance += outstanding_amount
            customer.save(update_fields=["current_balance", "updated_at"])

        logger.info(f"Created CustomerReceivable {ar_num} for invoice {sales_invoice.invoice_number} (${outstanding_amount} outstanding)")
        return receivable

    @transaction.atomic
    def apply_return_credit_to_receivable(
        self,
        tenant: Any,
        receivable: CustomerReceivable,
        return_credit_amount: Decimal | float | int,
        user: Any | None = None,
    ) -> CustomerReceivable:
        """Apply customer return credit / store credit against an open receivable obligation."""
        rx = CustomerReceivable.objects.select_for_update().get(pk=receivable.pk, tenant=tenant)
        customer = Customer.objects.select_for_update().get(pk=rx.customer.pk, tenant=tenant)

        amount_dec = Decimal(str(return_credit_amount))
        rx.credit_amount += amount_dec
        rx.recalculate_balances()
        rx.save(update_fields=["credit_amount", "outstanding_amount", "status", "updated_at"])

        # Reduce customer debt balance
        customer.current_balance -= amount_dec
        customer.save(update_fields=["current_balance", "updated_at"])

        logger.info(f"Applied return credit ${amount_dec} to CustomerReceivable {rx.receivable_number}")
        return rx
