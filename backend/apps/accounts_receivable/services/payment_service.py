"""CustomerPaymentService managing customer payments, multi-receivable allocations, overpayment rules, and reversals."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.accounts_receivable.exceptions import (
    InvalidARStateError,
    OverpaymentRejectedError,
    PaymentAlreadyReversedError,
)
from apps.accounts_receivable.models import (
    ARPaymentMethod,
    ARPaymentStatus,
    CustomerPayment,
    CustomerPaymentAllocation,
    CustomerReceivable,
    OverpaymentPolicy,
)
from apps.accounts_receivable.repositories import CustomerPaymentRepository
from apps.accounts_receivable.services.number_generator import ARNumberGenerator
from apps.accounts_receivable.validators import validate_allocation_amount
from apps.branches.models import Branch
from apps.companies.models import Company
from apps.customers.models import Customer

logger = logging.getLogger(__name__)


class CustomerPaymentService:
    """Service layer managing CustomerPayment posting, multi-receivable allocation, overpayment handling, and payment reversals."""

    def __init__(
        self,
        repository: CustomerPaymentRepository | None = None,
        number_generator: ARNumberGenerator | None = None,
    ) -> None:
        self.repository = repository or CustomerPaymentRepository()
        self.number_generator = number_generator or ARNumberGenerator()

    @transaction.atomic
    def post_customer_payment(
        self,
        tenant: Any,
        company: Company,
        customer: Customer,
        amount: Decimal | float | int,
        payment_method: str = ARPaymentMethod.CASH,
        allocations_data: list[dict[str, Any]] | None = None,
        branch: Branch | None = None,
        reference_number: str = "",
        overpayment_policy: str = OverpaymentPolicy.ALLOW_AS_CUSTOMER_CREDIT,
        idempotency_key: str = "",
        user: Any | None = None,
        notes: str = "",
    ) -> CustomerPayment:
        """Post a customer payment and allocate across one or multiple open customer receivables."""
        if idempotency_key:
            existing = self.repository.find_by_idempotency_key(tenant, idempotency_key)
            if existing:
                logger.info(f"Duplicate CustomerPayment request suppressed for key: {idempotency_key}")
                return existing

        total_amount = Decimal(str(amount))
        if total_amount <= Decimal("0.0000"):
            raise ValueError("Customer payment amount must be greater than zero.")

        cust = Customer.objects.select_for_update().get(pk=customer.pk, tenant=tenant)
        pmt_num = self.number_generator.generate_payment_number(tenant)

        payment = self.repository.create(
            tenant=tenant,
            company=company,
            branch=branch,
            customer=cust,
            payment_number=pmt_num,
            payment_date=timezone.now().date(),
            payment_method=payment_method,
            amount=total_amount,
            allocated_amount=Decimal("0.0000"),
            unallocated_amount=total_amount,
            reference_number=reference_number,
            status=ARPaymentStatus.POSTED,
            posted_by=user,
            idempotency_key=idempotency_key,
            notes=notes,
            created_by=user,
        )

        total_allocated = Decimal("0.0000")

        if allocations_data:
            for item in allocations_data:
                rx_id = item["receivable_id"]
                alloc_amount = Decimal(str(item["allocated_amount"]))

                receivable = CustomerReceivable.objects.select_for_update().get(pk=rx_id, customer=cust, tenant=tenant)
                validate_allocation_amount(alloc_amount, receivable.outstanding_amount)

                CustomerPaymentAllocation.objects.create(
                    tenant=tenant,
                    payment=payment,
                    receivable=receivable,
                    allocated_amount=alloc_amount,
                    allocation_date=timezone.now().date(),
                )

                receivable.paid_amount += alloc_amount
                receivable.recalculate_balances()
                receivable.save(update_fields=["paid_amount", "outstanding_amount", "status", "updated_at"])

                total_allocated += alloc_amount

        unallocated = total_amount - total_allocated
        if unallocated < Decimal("0.0000"):
            raise ValueError("Total allocated amount exceeds payment total amount.")

        if unallocated > Decimal("0.0000") and overpayment_policy == OverpaymentPolicy.REJECT:
            raise OverpaymentRejectedError(f"Unallocated overpayment of ${unallocated} rejected by policy.")

        payment.allocated_amount = total_allocated
        payment.unallocated_amount = unallocated
        if total_allocated >= total_amount:
            payment.status = ARPaymentStatus.FULLY_ALLOCATED
        elif total_allocated > Decimal("0.0000"):
            payment.status = ARPaymentStatus.PARTIALLY_ALLOCATED
        else:
            payment.status = ARPaymentStatus.POSTED
        payment.save(update_fields=["allocated_amount", "unallocated_amount", "status", "updated_at"])

        # Reduce customer debt balance
        cust.current_balance -= total_amount
        cust.save(update_fields=["current_balance", "updated_at"])

        logger.info(f"Successfully posted CustomerPayment {pmt_num} (${total_amount}) for customer {cust.english_name}")
        return payment

    @transaction.atomic
    def reverse_customer_payment(
        self,
        tenant: Any,
        payment: CustomerPayment,
        reversal_reason: str,
        user: Any | None = None,
    ) -> CustomerPayment:
        """Reverse a posted customer payment, restoring receivable outstanding balances and customer debt."""
        pmt = CustomerPayment.objects.select_for_update().get(pk=payment.pk, tenant=tenant)
        if pmt.status == ARPaymentStatus.REVERSED:
            raise PaymentAlreadyReversedError("Payment has already been reversed.")

        cust = Customer.objects.select_for_update().get(pk=pmt.customer.pk, tenant=tenant)

        # Reverse allocations against receivables
        for alloc in pmt.allocations.select_related("receivable"):
            rx = alloc.receivable
            rx = CustomerReceivable.objects.select_for_update().get(pk=rx.pk, tenant=tenant)
            rx.paid_amount -= alloc.allocated_amount
            rx.recalculate_balances()
            rx.save(update_fields=["paid_amount", "outstanding_amount", "status", "updated_at"])

        pmt.status = ARPaymentStatus.REVERSED
        pmt.reversed_at = timezone.now()
        pmt.reversed_by = user
        pmt.reversal_reason = reversal_reason
        pmt.save(update_fields=["status", "reversed_at", "reversed_by", "reversal_reason", "updated_at"])

        # Restore customer debt balance
        cust.current_balance += pmt.amount
        cust.save(update_fields=["current_balance", "updated_at"])

        logger.info(f"Reversed CustomerPayment {pmt.payment_number} (${pmt.amount}) for customer {cust.english_name}")
        return pmt
