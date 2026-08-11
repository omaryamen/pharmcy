"""Query selector layer for Customer Returns & Refunds analytics."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db.models import Count, Q, QuerySet, Sum

from apps.sales_returns.models import (
    CustomerRefund,
    CustomerReturn,
    ReturnStatus,
)


class ReturnsSelector:
    """Selector providing search, filtering, and reporting analytics for customer returns and refunds."""

    def list_customer_returns(
        self,
        tenant: Any,
        *,
        company_id: str | None = None,
        branch_id: str | None = None,
        warehouse_id: str | None = None,
        customer_id: str | None = None,
        sales_invoice_id: str | None = None,
        status: str | None = None,
        return_reason: str | None = None,
        date_from: Any | None = None,
        date_to: Any | None = None,
        search: str | None = None,
    ) -> QuerySet[CustomerReturn]:
        qs = (
            CustomerReturn.objects.filter(tenant=tenant)
            .select_related("company", "branch", "warehouse", "customer", "sales_invoice", "created_by", "approved_by", "inspected_by")
            .prefetch_related("lines__medicine", "lines__batch", "lines__storage_location", "refunds")
        )

        if company_id:
            qs = qs.filter(company_id=company_id)
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        if sales_invoice_id:
            qs = qs.filter(sales_invoice_id=sales_invoice_id)
        if status:
            qs = qs.filter(status=status)
        if return_reason:
            qs = qs.filter(return_reason=return_reason)
        if date_from:
            qs = qs.filter(return_date__gte=date_from)
        if date_to:
            qs = qs.filter(return_date__lte=date_to)
        if search:
            qs = qs.filter(
                Q(return_number__icontains=search)
                | Q(sales_invoice__invoice_number__icontains=search)
                | Q(customer__english_name__icontains=search)
                | Q(customer__first_name__icontains=search)
            )

        return qs

    def list_customer_refunds(
        self,
        tenant: Any,
        *,
        customer_id: str | None = None,
        customer_return_id: str | None = None,
        status: str | None = None,
    ) -> QuerySet[CustomerRefund]:
        qs = CustomerRefund.objects.filter(tenant=tenant).select_related("customer_return", "customer", "sales_invoice", "created_by", "processed_by")
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        if customer_return_id:
            qs = qs.filter(customer_return_id=customer_return_id)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_return_analytics(
        self,
        tenant: Any,
        *,
        company_id: str | None = None,
        branch_id: str | None = None,
        date_from: Any | None = None,
        date_to: Any | None = None,
    ) -> dict[str, Any]:
        """Calculate return metrics: total returns, total refund value, store credit issued, and return reasons breakdown."""
        qs = CustomerReturn.objects.filter(tenant=tenant)
        if company_id:
            qs = qs.filter(company_id=company_id)
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        if date_from:
            qs = qs.filter(return_date__gte=date_from)
        if date_to:
            qs = qs.filter(return_date__lte=date_to)

        total_returns = qs.count()
        accepted_returns = qs.filter(status__in=[ReturnStatus.ACCEPTED, ReturnStatus.REFUNDED, ReturnStatus.STORE_CREDIT_ISSUED]).count()
        rejected_returns = qs.filter(status=ReturnStatus.REJECTED).count()

        total_refunded = qs.aggregate(total=Sum("refund_amount"))["total"] or Decimal("0.0000")
        total_store_credit = qs.aggregate(total=Sum("store_credit_amount"))["total"] or Decimal("0.0000")

        reasons_breakdown = dict(
            qs.values_list("return_reason").annotate(total=Count("id"))
        )

        return {
            "total_return_requests": total_returns,
            "accepted_returns_count": accepted_returns,
            "rejected_returns_count": rejected_returns,
            "total_refunded_amount": str(total_refunded),
            "total_store_credit_amount": str(total_store_credit),
            "return_reasons_breakdown": reasons_breakdown,
        }
