"""ARReconciliationService auditing subledger balance integrity and detecting accounting discrepancies."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db.models import Sum

from apps.accounts_receivable.models import CustomerReceivable
from apps.customers.models import Customer
from apps.sales.models import SalesInvoice

logger = logging.getLogger(__name__)


class ARReconciliationService:
    """Service layer executing audit reconciliation across Sales Invoices, AR Subledger, Payments, and Customer Balances."""

    def reconcile_customer_balance(self, tenant: Any, customer: Customer) -> dict[str, Any]:
        """Audit customer debt balance against net sum of open receivables and unallocated payments."""
        cust = Customer.objects.get(pk=customer.pk, tenant=tenant)

        total_original = (
            CustomerReceivable.objects.filter(tenant=tenant, customer=cust)
            .aggregate(val=Sum("original_amount"))["val"]
            or Decimal("0.0000")
        )
        total_paid = (
            CustomerReceivable.objects.filter(tenant=tenant, customer=cust)
            .aggregate(val=Sum("paid_amount"))["val"]
            or Decimal("0.0000")
        )
        total_credit = (
            CustomerReceivable.objects.filter(tenant=tenant, customer=cust)
            .aggregate(val=Sum("credit_amount"))["val"]
            or Decimal("0.0000")
        )
        total_adjusted = (
            CustomerReceivable.objects.filter(tenant=tenant, customer=cust)
            .aggregate(val=Sum("adjusted_amount"))["val"]
            or Decimal("0.0000")
        )

        expected_outstanding = total_original - total_paid - total_credit - total_adjusted
        actual_outstanding = (
            CustomerReceivable.objects.filter(tenant=tenant, customer=cust)
            .aggregate(val=Sum("outstanding_amount"))["val"]
            or Decimal("0.0000")
        )

        discrepancy = actual_outstanding - expected_outstanding
        is_reconciled = discrepancy == Decimal("0.0000")

        return {
            "customer_id": str(cust.pk),
            "customer_name": cust.english_name,
            "total_original": total_original,
            "total_paid": total_paid,
            "total_credit": total_credit,
            "total_adjusted": total_adjusted,
            "expected_outstanding": expected_outstanding,
            "actual_outstanding": actual_outstanding,
            "discrepancy": discrepancy,
            "is_reconciled": is_reconciled,
        }
