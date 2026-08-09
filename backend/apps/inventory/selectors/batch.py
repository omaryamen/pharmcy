"""Batch selector functions for queries, expiry tracking, and FEFO readiness."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from django.db.models import Q, QuerySet
from django.utils import timezone

from apps.inventory.models import Batch
from apps.inventory.repositories import BatchRepository


class BatchSelector:
    def __init__(self) -> None:
        self.repository = BatchRepository()

    def list_batches(
        self,
        tenant,
        *,
        company_id: str | None = None,
        medicine_id: str | None = None,
        supplier_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> QuerySet[Batch]:
        qs = self.repository.filter(tenant=tenant).select_related("company", "medicine", "supplier", "tenant")

        if company_id:
            qs = qs.filter(company_id=company_id)
        if medicine_id:
            qs = qs.filter(medicine_id=medicine_id)
        if supplier_id:
            qs = qs.filter(supplier_id=supplier_id)
        if status:
            qs = qs.filter(status=status)

        if search:
            qs = qs.filter(
                Q(batch_number__icontains=search)
                | Q(lot_number__icontains=search)
                | Q(medicine__english_name__icontains=search)
                | Q(medicine__arabic_name__icontains=search)
                | Q(medicine__brand_name__icontains=search)
                | Q(medicine__generic_name__icontains=search)
                | Q(registration_number__icontains=search)
            )

        return qs

    def get_batch_detail(self, tenant, batch_id: str) -> Batch | None:
        return (
            self.repository.filter(tenant=tenant, pk=batch_id)
            .select_related("company", "medicine", "supplier", "tenant")
            .prefetch_related("inventory_items")
            .first()
        )

    def get_expired_batches(self, tenant, *, medicine_id: str | None = None) -> QuerySet[Batch]:
        today = timezone.now().date()
        qs = self.repository.filter(tenant=tenant, expiry_date__lt=today).select_related("medicine", "supplier")
        if medicine_id:
            qs = qs.filter(medicine_id=medicine_id)
        return qs

    def get_expiring_soon_batches(self, tenant, days: int = 90, *, medicine_id: str | None = None) -> QuerySet[Batch]:
        today = timezone.now().date()
        target_date = today + timedelta(days=days)
        qs = self.repository.filter(tenant=tenant, expiry_date__gte=today, expiry_date__lte=target_date).select_related(
            "medicine", "supplier"
        )
        if medicine_id:
            qs = qs.filter(medicine_id=medicine_id)
        return qs

    def get_available_batches_fefo(self, tenant, medicine_id: str, warehouse_id: str | None = None) -> QuerySet[Batch]:
        """First Expired, First Out (FEFO) query selector returning active non-expired batches ordered by earliest expiry."""
        today = timezone.now().date()
        qs = (
            self.repository.filter(
                tenant=tenant,
                medicine_id=medicine_id,
                status="active",
                expiry_date__gte=today,
            )
            .select_related("medicine", "company")
            .order_by("expiry_date", "batch_number")
        )

        if warehouse_id:
            qs = qs.filter(inventory_items__warehouse_id=warehouse_id, inventory_items__on_hand_quantity__gt=0).distinct()

        return qs
