"""Query selector layer for BatchRecall search and reporting."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.alerts.models import BatchRecall


class BatchRecallSelector:
    """Selector providing query methods for BatchRecall."""

    def list_recalls(
        self,
        tenant: Any,
        *,
        company_id: str | None = None,
        medicine_id: str | None = None,
        batch_id: str | None = None,
        recall_class: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> QuerySet[BatchRecall]:
        qs = (
            BatchRecall.objects.filter(tenant=tenant)
            .select_related("company", "medicine", "batch", "initiated_by", "completed_by")
        )

        if company_id:
            qs = qs.filter(company_id=company_id)
        if medicine_id:
            qs = qs.filter(medicine_id=medicine_id)
        if batch_id:
            qs = qs.filter(batch_id=batch_id)
        if recall_class:
            qs = qs.filter(recall_class=recall_class)
        if status:
            qs = qs.filter(status=status)
        if search:
            qs = qs.filter(recall_number__icontains=search) | qs.filter(reason__icontains=search)

        return qs

    def get_recall_by_id(self, tenant: Any, recall_id: str) -> BatchRecall | None:
        return (
            BatchRecall.objects.filter(tenant=tenant, pk=recall_id)
            .select_related("company", "medicine", "batch", "initiated_by", "completed_by")
            .first()
        )
