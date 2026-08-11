"""Query selector layer for Accounts Payable search, aging, and supplier balances."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db.models import Count, Q, QuerySet, Sum
from django.utils import timezone

from apps.accounts_payable.models import (
    AccountsPayableEntry,
    APStatus,
    InvoiceStatus,
    SupplierInvoice,
    SupplierPayment,
)
from apps.purchase_returns.models import SupplierCreditNote


class AccountsPayableSelector:
    """Selector providing query methods, AP aging calculations, and supplier balance summaries."""

    def list_supplier_invoices(
        self,
        tenant: Any,
        *,
        company_id: str | None = None,
        branch_id: str | None = None,
        supplier_id: str | None = None,
        purchase_order_id: str | None = None,
        goods_receipt_id: str | None = None,
        status: str | None = None,
        match_status: str | None = None,
        due_date_before: Any | None = None,
        search: str | None = None,
    ) -> QuerySet[SupplierInvoice]:
        qs = (
            SupplierInvoice.objects.filter(tenant=tenant)
            .select_related("company", "branch", "supplier", "purchase_order", "goods_receipt", "created_by", "verified_by", "approved_by")
            .prefetch_related("lines__medicine", "payments", "credit_applications", "disputes")
        )

        if company_id:
            qs = qs.filter(company_id=company_id)
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        if supplier_id:
            qs = qs.filter(supplier_id=supplier_id)
        if purchase_order_id:
            qs = qs.filter(purchase_order_id=purchase_order_id)
        if goods_receipt_id:
            qs = qs.filter(goods_receipt_id=goods_receipt_id)
        if status:
            qs = qs.filter(status=status)
        if match_status:
            qs = qs.filter(match_status=match_status)
        if due_date_before:
            qs = qs.filter(due_date__lte=due_date_before)
        if search:
            qs = qs.filter(
                Q(invoice_number__icontains=search)
                | Q(supplier_invoice_number__icontains=search)
                | Q(supplier__legal_name__icontains=search)
            )

        return qs

    def get_supplier_invoice_by_id(self, tenant: Any, invoice_id: str) -> SupplierInvoice | None:
        return (
            SupplierInvoice.objects.filter(tenant=tenant, pk=invoice_id)
            .select_related("company", "branch", "supplier", "purchase_order", "goods_receipt", "created_by", "verified_by", "approved_by")
            .prefetch_related("lines__medicine", "payments", "credit_applications", "disputes")
            .first()
        )

    def list_accounts_payable_entries(
        self,
        tenant: Any,
        *,
        supplier_id: str | None = None,
        status: str | None = None,
    ) -> QuerySet[AccountsPayableEntry]:
        qs = AccountsPayableEntry.objects.filter(tenant=tenant).select_related("company", "branch", "supplier", "supplier_invoice")
        if supplier_id:
            qs = qs.filter(supplier_id=supplier_id)
        if status:
            qs = qs.filter(status=status)
        return qs

    def calculate_ap_aging(self, tenant: Any, supplier_id: str | None = None) -> dict[str, Any]:
        """Calculate Accounts Payable aging breakdown across standard aging brackets."""
        today = timezone.now().date()
        qs = AccountsPayableEntry.objects.filter(tenant=tenant, status__in=[APStatus.OPEN, APStatus.PARTIALLY_PAID, APStatus.OVERDUE])
        if supplier_id:
            qs = qs.filter(supplier_id=supplier_id)

        buckets = {
            "current": Decimal("0.0000"),
            "days_1_30": Decimal("0.0000"),
            "days_31_60": Decimal("0.0000"),
            "days_61_90": Decimal("0.0000"),
            "days_90_plus": Decimal("0.0000"),
            "total_outstanding": Decimal("0.0000"),
        }

        for entry in qs:
            bal = entry.outstanding_amount
            buckets["total_outstanding"] += bal

            if entry.due_date >= today:
                buckets["current"] += bal
            else:
                overdue_days = (today - entry.due_date).days
                if overdue_days <= 30:
                    buckets["days_1_30"] += bal
                elif overdue_days <= 60:
                    buckets["days_31_60"] += bal
                elif overdue_days <= 90:
                    buckets["days_61_90"] += bal
                else:
                    buckets["days_90_plus"] += bal

        return {k: str(v) for k, v in buckets.items()}

    def get_supplier_balance_summary(self, tenant: Any, supplier_id: str | None = None) -> dict[str, Any]:
        """Calculate total purchases, credit notes, payments, and net outstanding AP balance."""
        inv_qs = SupplierInvoice.objects.filter(tenant=tenant, status__in=[InvoiceStatus.POSTED, InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.PAID, InvoiceStatus.OVERDUE])
        pmt_qs = SupplierPayment.objects.filter(tenant=tenant, status="posted")
        crn_qs = SupplierCreditNote.objects.filter(tenant=tenant)

        if supplier_id:
            inv_qs = inv_qs.filter(supplier_id=supplier_id)
            pmt_qs = pmt_qs.filter(supplier_id=supplier_id)
            crn_qs = crn_qs.filter(supplier_id=supplier_id)

        total_invoiced = inv_qs.aggregate(total=Sum("grand_total"))["total"] or Decimal("0.0000")
        total_paid = pmt_qs.aggregate(total=Sum("amount"))["total"] or Decimal("0.0000")
        total_credits = crn_qs.aggregate(total=Sum("net_credit_value"))["total"] or Decimal("0.0000")

        ap_qs = AccountsPayableEntry.objects.filter(tenant=tenant, status__in=[APStatus.OPEN, APStatus.PARTIALLY_PAID, APStatus.OVERDUE])
        if supplier_id:
            ap_qs = ap_qs.filter(supplier_id=supplier_id)

        outstanding = ap_qs.aggregate(total=Sum("outstanding_amount"))["total"] or Decimal("0.0000")

        today = timezone.now().date()
        overdue = ap_qs.filter(due_date__lt=today).aggregate(total=Sum("outstanding_amount"))["total"] or Decimal("0.0000")

        return {
            "total_invoiced_purchases": str(total_invoiced),
            "total_payments_made": str(total_paid),
            "total_supplier_credits": str(total_credits),
            "outstanding_ap_balance": str(outstanding),
            "overdue_ap_balance": str(overdue),
        }
