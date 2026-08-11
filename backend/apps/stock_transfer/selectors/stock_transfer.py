"""Selector queries for StockTransfer reporting and data retrieval."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db.models import Q, Sum

from apps.stock_transfer.models import (
    StockTransfer,
    StockTransferDiscrepancy,
    StockTransferHistory,
    StockTransferLine,
    TransferStatus,
)


class StockTransferSelector:
    """Selector queries for StockTransfer search, filtering, detail lookups, discrepancies, and reporting."""

    def list_transfers(
        self,
        tenant: Any,
        *,
        company_id: str | None = None,
        source_branch_id: str | None = None,
        destination_branch_id: str | None = None,
        source_warehouse_id: str | None = None,
        destination_warehouse_id: str | None = None,
        transfer_type: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        created_by_id: str | None = None,
        date_from: Any | None = None,
        date_to: Any | None = None,
        search: str | None = None,
    ):
        qs = (
            StockTransfer.objects.filter(tenant=tenant)
            .select_related(
                "company",
                "source_branch",
                "destination_branch",
                "source_warehouse",
                "destination_warehouse",
                "source_location",
                "destination_location",
                "requested_by",
                "approved_by",
                "dispatched_by",
                "received_by",
            )
            .prefetch_related("lines")
        )

        if company_id:
            qs = qs.filter(company_id=company_id)
        if source_branch_id:
            qs = qs.filter(source_branch_id=source_branch_id)
        if destination_branch_id:
            qs = qs.filter(destination_branch_id=destination_branch_id)
        if source_warehouse_id:
            qs = qs.filter(source_warehouse_id=source_warehouse_id)
        if destination_warehouse_id:
            qs = qs.filter(destination_warehouse_id=destination_warehouse_id)
        if transfer_type:
            qs = qs.filter(transfer_type=transfer_type)
        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)
        if created_by_id:
            qs = qs.filter(requested_by_id=created_by_id)
        if date_from:
            qs = qs.filter(created_at__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__lte=date_to)

        if search:
            qs = qs.filter(
                Q(transfer_number__icontains=search)
                | Q(reason__icontains=search)
                | Q(notes__icontains=search)
                | Q(source_warehouse__name__icontains=search)
                | Q(destination_warehouse__name__icontains=search)
            )

        return qs.order_by("-created_at")

    def get_transfer_by_id(self, tenant: Any, transfer_id: str) -> StockTransfer | None:
        return (
            StockTransfer.objects.filter(tenant=tenant, pk=transfer_id)
            .select_related(
                "company",
                "source_branch",
                "destination_branch",
                "source_warehouse",
                "destination_warehouse",
                "source_location",
                "destination_location",
                "requested_by",
                "approved_by",
                "dispatched_by",
                "received_by",
                "cancelled_by",
            )
            .prefetch_related(
                "lines__medicine",
                "lines__batch",
                "lines__source_location",
                "lines__destination_location",
                "discrepancies",
                "history",
            )
            .first()
        )

    def get_in_transit_transfers(self, tenant: Any):
        return self.list_transfers(tenant=tenant, status=TransferStatus.IN_TRANSIT)

    def get_pending_transfers(self, tenant: Any):
        return (
            StockTransfer.objects.filter(
                tenant=tenant,
                status__in=[TransferStatus.REQUESTED, TransferStatus.PENDING_APPROVAL, TransferStatus.APPROVED],
            )
            .select_related("source_warehouse", "destination_warehouse", "requested_by")
            .order_by("-created_at")
        )

    def get_discrepancies(self, tenant: Any, *, transfer_id: str | None = None):
        qs = StockTransferDiscrepancy.objects.filter(tenant=tenant).select_related(
            "stock_transfer", "transfer_line", "expected_medicine", "received_medicine", "expected_batch", "received_batch", "reported_by", "reviewed_by"
        )
        if transfer_id:
            qs = qs.filter(stock_transfer_id=transfer_id)
        return qs.order_by("-created_at")

    def get_transfer_history(self, tenant: Any, transfer_id: str):
        return (
            StockTransferHistory.objects.filter(tenant=tenant, stock_transfer_id=transfer_id)
            .select_related("performed_by")
            .order_by("timestamp")
        )

    def get_transfer_statistics(self, tenant: Any, *, company_id: str | None = None, warehouse_id: str | None = None) -> dict[str, Any]:
        qs = StockTransfer.objects.filter(tenant=tenant)
        if company_id:
            qs = qs.filter(company_id=company_id)
        if warehouse_id:
            qs = qs.filter(Q(source_warehouse_id=warehouse_id) | Q(destination_warehouse_id=warehouse_id))

        total_count = qs.count()
        in_transit = qs.filter(status=TransferStatus.IN_TRANSIT).count()
        pending = qs.filter(status__in=[TransferStatus.REQUESTED, TransferStatus.PENDING_APPROVAL]).count()
        completed = qs.filter(status__in=[TransferStatus.RECEIVED, TransferStatus.CLOSED]).count()
        discrepancies_count = StockTransferDiscrepancy.objects.filter(tenant=tenant).count()

        total_value = qs.filter(status__in=[TransferStatus.DISPATCHED, TransferStatus.IN_TRANSIT, TransferStatus.RECEIVED, TransferStatus.CLOSED]).aggregate(
            v=Sum("total_cost")
        )["v"] or Decimal("0.0000")

        return {
            "total_transfers": total_count,
            "in_transit_transfers": in_transit,
            "pending_approval_transfers": pending,
            "completed_transfers": completed,
            "total_discrepancies": discrepancies_count,
            "total_transfer_value": total_value,
        }
