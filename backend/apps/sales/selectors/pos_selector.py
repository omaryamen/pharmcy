"""Query selector layer for POS barcode lookup, sales search, and profitability analytics."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db.models import Count, Q, QuerySet, Sum

from apps.medicines.models import Medicine
from apps.sales.models import RegisterSession, SalesInvoice, SalesPayment, SalesStatus


class PosSelector:
    """Selector providing fast barcode lookups, sales query filters, and gross profit analytics."""

    def barcode_or_sku_lookup(self, tenant: Any, query: str) -> QuerySet[Medicine]:
        """Fast lookup for medicine master records by barcode, SKU, code, or name."""
        q = query.strip()
        return Medicine.objects.filter(
            tenant=tenant,
            status="active",
        ).filter(
            Q(sku__iexact=q)
            | Q(code__iexact=q)
            | Q(barcode__iexact=q)
            | Q(english_name__icontains=q)
            | Q(arabic_name__icontains=q)
        ).select_related("category_ref", "manufacturer_ref")

    def list_sales_invoices(
        self,
        tenant: Any,
        *,
        company_id: str | None = None,
        branch_id: str | None = None,
        warehouse_id: str | None = None,
        customer_id: str | None = None,
        cashier_id: str | None = None,
        status: str | None = None,
        payment_status: str | None = None,
        date_from: Any | None = None,
        date_to: Any | None = None,
        search: str | None = None,
    ) -> QuerySet[SalesInvoice]:
        qs = (
            SalesInvoice.objects.filter(tenant=tenant)
            .select_related("company", "branch", "warehouse", "customer", "cashier", "register_session")
            .prefetch_related("lines__medicine", "lines__batch", "lines__storage_location", "payments")
        )

        if company_id:
            qs = qs.filter(company_id=company_id)
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        if cashier_id:
            qs = qs.filter(cashier_id=cashier_id)
        if status:
            qs = qs.filter(status=status)
        if payment_status:
            qs = qs.filter(payment_status=payment_status)
        if date_from:
            qs = qs.filter(invoice_date__gte=date_from)
        if date_to:
            qs = qs.filter(invoice_date__lte=date_to)
        if search:
            qs = qs.filter(
                Q(invoice_number__icontains=search)
                | Q(customer__legal_name__icontains=search)
            )

        return qs

    def get_sales_analytics(
        self,
        tenant: Any,
        *,
        company_id: str | None = None,
        branch_id: str | None = None,
        date_from: Any | None = None,
        date_to: Any | None = None,
    ) -> dict[str, Any]:
        """Calculate gross sales, discount, tax, net sales, total cost, gross profit, and cashier statistics."""
        qs = SalesInvoice.objects.filter(tenant=tenant, status__in=[SalesStatus.COMPLETED, SalesStatus.PAID, SalesStatus.CREDIT])
        if company_id:
            qs = qs.filter(company_id=company_id)
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        if date_from:
            qs = qs.filter(invoice_date__gte=date_from)
        if date_to:
            qs = qs.filter(invoice_date__lte=date_to)

        total_sales = qs.count()
        gross_sales = qs.aggregate(total=Sum("grand_total"))["total"] or Decimal("0.0000")
        total_discount = qs.aggregate(total=Sum("discount"))["total"] or Decimal("0.0000")
        total_tax = qs.aggregate(total=Sum("tax"))["total"] or Decimal("0.0000")

        # Line profit aggregation
        profit_agg = (
            SalesInvoice.objects.filter(tenant=tenant, status__in=[SalesStatus.COMPLETED, SalesStatus.PAID, SalesStatus.CREDIT])
            .filter(pk__in=qs.values_list("pk", flat=True))
            .aggregate(profit=Sum("lines__profit_amount"))
        )
        total_profit = profit_agg["profit"] or Decimal("0.0000")

        payment_method_breakdown = dict(
            SalesPayment.objects.filter(tenant=tenant, sales_invoice__in=qs, status="posted")
            .values_list("payment_method")
            .annotate(total=Sum("amount"))
        )

        return {
            "total_sales_count": total_sales,
            "gross_sales_amount": str(gross_sales),
            "total_discount_amount": str(total_discount),
            "total_tax_amount": str(total_tax),
            "total_gross_profit": str(total_profit),
            "payment_methods_breakdown": {k: str(v) for k, v in payment_method_breakdown.items()},
        }
