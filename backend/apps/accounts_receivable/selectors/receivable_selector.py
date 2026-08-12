"""Query selector layer for Customer Accounts Receivable (AR) reporting, aging, and customer ledger statements."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db.models import Q, QuerySet, Sum
from django.utils import timezone

from apps.accounts_receivable.models import (
    ARPaymentStatus,
    ARStatus,
    CustomerPayment,
    CustomerReceivable,
)


class ReceivableSelector:
    """Selector providing search, filtering, aging buckets, customer statements, and AR analytics."""

    def list_receivables(
        self,
        tenant: Any,
        *,
        company_id: str | None = None,
        branch_id: str | None = None,
        customer_id: str | None = None,
        status: str | None = None,
        is_overdue: bool | None = None,
        search: str | None = None,
    ) -> QuerySet[CustomerReceivable]:
        qs = (
            CustomerReceivable.objects.filter(tenant=tenant)
            .select_related("company", "branch", "customer", "sales_invoice")
            .prefetch_related("allocations", "adjustments", "write_offs", "disputes")
        )

        if company_id:
            qs = qs.filter(company_id=company_id)
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        if status:
            qs = qs.filter(status=status)
        if is_overdue:
            qs = qs.filter(due_date__lt=timezone.now().date(), outstanding_amount__gt=Decimal("0.0000"))

        if search:
            qs = qs.filter(
                Q(receivable_number__icontains=search)
                | Q(customer__english_name__icontains=search)
                | Q(customer__code__icontains=search)
                | Q(sales_invoice__invoice_number__icontains=search)
            )

        return qs

    def list_payments(
        self,
        tenant: Any,
        *,
        customer_id: str | None = None,
        status: str | None = None,
    ) -> QuerySet[CustomerPayment]:
        qs = CustomerPayment.objects.filter(tenant=tenant).select_related("company", "branch", "customer", "posted_by", "approved_by").prefetch_related("allocations__receivable")
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_ar_aging_report(
        self,
        tenant: Any,
        *,
        company_id: str | None = None,
        customer_id: str | None = None,
    ) -> dict[str, Any]:
        """Calculate AR aging analysis buckets (Current, 1-30, 31-60, 61-90, 90+ days) based on payment due date."""
        today = timezone.now().date()
        qs = CustomerReceivable.objects.filter(tenant=tenant, outstanding_amount__gt=Decimal("0.0000")).exclude(status__in=[ARStatus.PAID, ARStatus.CANCELLED, ARStatus.WRITTEN_OFF, ARStatus.REVERSED])

        if company_id:
            qs = qs.filter(company_id=company_id)
        if customer_id:
            qs = qs.filter(customer_id=customer_id)

        current = Decimal("0.0000")
        days_1_30 = Decimal("0.0000")
        days_31_60 = Decimal("0.0000")
        days_61_90 = Decimal("0.0000")
        days_90_plus = Decimal("0.0000")

        for item in qs:
            due = item.due_date
            amount = item.outstanding_amount

            if due >= today:
                current += amount
            else:
                overdue_days = (today - due).days
                if overdue_days <= 30:
                    days_1_30 += amount
                elif overdue_days <= 60:
                    days_31_60 += amount
                elif overdue_days <= 90:
                    days_61_90 += amount
                else:
                    days_90_plus += amount

        total_outstanding = current + days_1_30 + days_31_60 + days_61_90 + days_90_plus

        return {
            "current": current,
            "days_1_30": days_1_30,
            "days_31_60": days_31_60,
            "days_61_90": days_61_90,
            "days_90_plus": days_90_plus,
            "total_outstanding": total_outstanding,
        }

    def get_customer_statement(
        self,
        tenant: Any,
        customer_id: str,
        *,
        start_date: Any = None,
        end_date: Any = None,
    ) -> dict[str, Any]:
        """Generate comprehensive customer ledger financial statement with chronological running balance."""
        from apps.customers.models import Customer
        customer = Customer.objects.get(pk=customer_id, tenant=tenant)

        receivables = CustomerReceivable.objects.filter(tenant=tenant, customer=customer).exclude(status=ARStatus.CANCELLED)
        payments = CustomerPayment.objects.filter(tenant=tenant, customer=customer, status=ARPaymentStatus.POSTED)

        if start_date:
            receivables = receivables.filter(invoice_date__gte=start_date)
            payments = payments.filter(payment_date__gte=start_date)
        if end_date:
            receivables = receivables.filter(invoice_date__lte=end_date)
            payments = payments.filter(payment_date__lte=end_date)

        opening_balance = Decimal(str(customer.opening_balance))
        running_balance = opening_balance

        entries = []

        for rx in receivables.order_by("invoice_date", "created_at"):
            debit = rx.original_amount
            credit = Decimal("0.0000")
            running_balance += debit

            entries.append({
                "date": rx.invoice_date,
                "type": "INVOICE",
                "reference": rx.receivable_number,
                "description": f"Sales Invoice {rx.sales_invoice.invoice_number if rx.sales_invoice else ''}",
                "debit": debit,
                "credit": credit,
                "running_balance": running_balance,
            })

        for pmt in payments.order_by("payment_date", "created_at"):
            debit = Decimal("0.0000")
            credit = pmt.amount
            running_balance -= credit

            entries.append({
                "date": pmt.payment_date,
                "type": "PAYMENT",
                "reference": pmt.payment_number,
                "description": f"Customer Payment via {pmt.payment_method}",
                "debit": debit,
                "credit": credit,
                "running_balance": running_balance,
            })

        # Sort combined statement entries chronologically
        entries.sort(key=lambda x: x["date"])

        # Re-compute exact running balance after sorting
        curr = opening_balance
        for e in entries:
            curr = curr + e["debit"] - e["credit"]
            e["running_balance"] = curr

        return {
            "customer_id": str(customer.pk),
            "customer_name": customer.english_name,
            "opening_balance": opening_balance,
            "total_debits": sum(e["debit"] for e in entries),
            "total_credits": sum(e["credit"] for e in entries),
            "closing_balance": curr,
            "statement_entries": entries,
        }

    def get_ar_statistics(self, tenant: Any, *, company_id: str | None = None) -> dict[str, Any]:
        """Calculate overall Accounts Receivable subledger metrics."""
        qs = CustomerReceivable.objects.filter(tenant=tenant).exclude(status=ARStatus.CANCELLED)
        if company_id:
            qs = qs.filter(company_id=company_id)

        total_receivables = qs.aggregate(val=Sum("original_amount"))["val"] or Decimal("0.0000")
        paid_receivables = qs.aggregate(val=Sum("paid_amount"))["val"] or Decimal("0.0000")
        outstanding_receivables = qs.aggregate(val=Sum("outstanding_amount"))["val"] or Decimal("0.0000")

        today = timezone.now().date()
        overdue_receivables = qs.filter(due_date__lt=today, outstanding_amount__gt=Decimal("0.0000")).aggregate(val=Sum("outstanding_amount"))["val"] or Decimal("0.0000")

        return {
            "total_receivables": total_receivables,
            "paid_receivables": paid_receivables,
            "outstanding_receivables": outstanding_receivables,
            "overdue_receivables": overdue_receivables,
        }
