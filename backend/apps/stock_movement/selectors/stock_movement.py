"""Selectors for querying and reporting StockMovement data."""

from __future__ import annotations

from typing import Any

from django.db.models import Q, QuerySet, Sum, Count
from django.utils import timezone

from apps.stock_movement.models import StockMovement, StockMovementLine


class StockMovementSelector:
    """Read-only selector for StockMovement queries and audit traceability reporting."""

    def list_movements(
        self,
        tenant: Any,
        *,
        company_id: str | None = None,
        branch_id: str | None = None,
        warehouse_id: str | None = None,
        source_warehouse_id: str | None = None,
        destination_warehouse_id: str | None = None,
        medicine_id: str | None = None,
        batch_id: str | None = None,
        movement_type: str | None = None,
        movement_status: str | None = None,
        reference_type: str | None = None,
        reference_id: str | None = None,
        date_from: Any | None = None,
        date_to: Any | None = None,
        search: str | None = None,
    ) -> QuerySet[StockMovement]:
        qs = StockMovement.objects.filter(tenant=tenant).select_related(
            "company",
            "branch",
            "warehouse",
            "source_warehouse",
            "destination_warehouse",
            "source_location",
            "destination_location",
            "medicine",
            "batch",
            "performed_by",
            "approved_by",
            "reversed_movement",
        ).prefetch_related("lines__medicine", "lines__batch", "lines__source_location", "lines__destination_location")

        if company_id:
            qs = qs.filter(company_id=company_id)
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        if warehouse_id:
            qs = qs.filter(Q(warehouse_id=warehouse_id) | Q(source_warehouse_id=warehouse_id) | Q(destination_warehouse_id=warehouse_id))
        if source_warehouse_id:
            qs = qs.filter(source_warehouse_id=source_warehouse_id)
        if destination_warehouse_id:
            qs = qs.filter(destination_warehouse_id=destination_warehouse_id)
        if medicine_id:
            qs = qs.filter(Q(medicine_id=medicine_id) | Q(lines__medicine_id=medicine_id)).distinct()
        if batch_id:
            qs = qs.filter(Q(batch_id=batch_id) | Q(lines__batch_id=batch_id)).distinct()
        if movement_type:
            qs = qs.filter(movement_type=movement_type)
        if movement_status:
            qs = qs.filter(movement_status=movement_status)
        if reference_type:
            qs = qs.filter(reference_type=reference_type)
        if reference_id:
            qs = qs.filter(reference_id=reference_id)
        if date_from:
            qs = qs.filter(created_at__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__lte=date_to)

        if search:
            qs = qs.filter(
                Q(movement_number__icontains=search)
                | Q(reference_number__icontains=search)
                | Q(reference_id__icontains=search)
                | Q(reason__icontains=search)
                | Q(notes__icontains=search)
                | Q(medicine__english_name__icontains=search)
                | Q(batch__batch_number__icontains=search)
                | Q(lines__medicine__english_name__icontains=search)
                | Q(lines__batch__batch_number__icontains=search)
            ).distinct()

        return qs

    def get_movement_by_id(self, tenant: Any, movement_id: str) -> StockMovement | None:
        return self.list_movements(tenant).filter(pk=movement_id).first()

    def get_movement_by_number(self, tenant: Any, movement_number: str) -> StockMovement | None:
        return self.list_movements(tenant).filter(movement_number=movement_number).first()

    def get_medicine_traceability(self, tenant: Any, medicine_id: str) -> QuerySet[StockMovementLine]:
        """Retrieve complete historical audit movement log for a specific medicine."""
        return StockMovementLine.objects.filter(
            tenant=tenant,
            medicine_id=medicine_id,
        ).select_related(
            "movement",
            "movement__warehouse",
            "movement__source_warehouse",
            "movement__destination_warehouse",
            "source_location",
            "destination_location",
            "batch",
            "movement__performed_by",
        ).order_by("-created_at")

    def get_batch_traceability(self, tenant: Any, batch_id: str) -> QuerySet[StockMovementLine]:
        """Retrieve complete historical audit movement log for a specific batch."""
        return StockMovementLine.objects.filter(
            tenant=tenant,
            batch_id=batch_id,
        ).select_related(
            "movement",
            "movement__warehouse",
            "source_location",
            "destination_location",
            "medicine",
            "movement__performed_by",
        ).order_by("-created_at")

    def get_movement_statistics(self, tenant: Any, company_id: str | None = None, warehouse_id: str | None = None) -> dict[str, Any]:
        qs = StockMovement.objects.filter(tenant=tenant)
        if company_id:
            qs = qs.filter(company_id=company_id)
        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)

        total_movements = qs.count()
        completed_movements = qs.filter(movement_status="completed").count()
        pending_movements = qs.filter(movement_status__in=["draft", "pending_approval", "approved"]).count()
        reversed_movements = qs.filter(movement_status="reversed").count()

        total_quantity_moved = qs.filter(movement_status="completed").aggregate(val=Sum("quantity"))["val"] or 0
        total_cost_moved = qs.filter(movement_status="completed").aggregate(val=Sum("total_cost"))["val"] or 0

        by_type = dict(
            qs.filter(movement_status="completed")
            .values_list("movement_type")
            .annotate(cnt=Count("id"))
        )

        return {
            "total_movements": total_movements,
            "completed_movements": completed_movements,
            "pending_movements": pending_movements,
            "reversed_movements": reversed_movements,
            "total_quantity_moved": total_quantity_moved,
            "total_cost_moved": total_cost_moved,
            "by_type": by_type,
        }
