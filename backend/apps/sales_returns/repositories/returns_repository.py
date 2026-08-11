"""Repository layer for Customer Returns persistence."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.sales_returns.models import CustomerRefund, CustomerReturn, CustomerReturnLine


class CustomerReturnRepository:
    """Repository encapsulating persistence operations for CustomerReturn."""

    def get_queryset(self, tenant: Any) -> QuerySet[CustomerReturn]:
        return CustomerReturn.objects.filter(tenant=tenant)

    def find_by_id(self, tenant: Any, return_id: str) -> CustomerReturn | None:
        return self.get_queryset(tenant).filter(pk=return_id).first()

    def find_by_idempotency_key(self, tenant: Any, key: str) -> CustomerReturn | None:
        if not key:
            return None
        return self.get_queryset(tenant).filter(idempotency_key=key).first()

    def create(self, tenant: Any, **kwargs: Any) -> CustomerReturn:
        return CustomerReturn.objects.create(tenant=tenant, **kwargs)


class CustomerRefundRepository:
    """Repository encapsulating persistence operations for CustomerRefund."""

    def get_queryset(self, tenant: Any) -> QuerySet[CustomerRefund]:
        return CustomerRefund.objects.filter(tenant=tenant)

    def create(self, tenant: Any, **kwargs: Any) -> CustomerRefund:
        return CustomerRefund.objects.create(tenant=tenant, **kwargs)
