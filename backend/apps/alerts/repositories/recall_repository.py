"""Repository layer for BatchRecall persistence."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.alerts.models import BatchRecall


class BatchRecallRepository:
    """Repository encapsulating persistence operations for BatchRecall."""

    def get_queryset(self, tenant: Any) -> QuerySet[BatchRecall]:
        return BatchRecall.objects.filter(tenant=tenant)

    def find_by_id(self, tenant: Any, recall_id: str) -> BatchRecall | None:
        return self.get_queryset(tenant).filter(pk=recall_id).first()

    def find_by_batch(self, tenant: Any, batch_id: str) -> BatchRecall | None:
        return self.get_queryset(tenant).filter(batch_id=batch_id).exclude(status="cancelled").first()

    def create(self, tenant: Any, **kwargs: Any) -> BatchRecall:
        return BatchRecall.objects.create(tenant=tenant, **kwargs)

    def update(self, recall: BatchRecall, **kwargs: Any) -> BatchRecall:
        for field, value in kwargs.items():
            setattr(recall, field, value)
        recall.save()
        return recall
