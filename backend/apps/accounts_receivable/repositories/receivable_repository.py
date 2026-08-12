"""Repository layer for CustomerReceivable and CustomerPayment persistence."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.accounts_receivable.models import CustomerPayment, CustomerReceivable


class CustomerReceivableRepository:
    """Repository encapsulating persistence operations for CustomerReceivable entity."""

    def get_queryset(self, tenant: Any) -> QuerySet[CustomerReceivable]:
        return CustomerReceivable.objects.filter(tenant=tenant)

    def find_by_id(self, tenant: Any, receivable_id: str) -> CustomerReceivable | None:
        return self.get_queryset(tenant).filter(pk=receivable_id).first()

    def find_by_sales_invoice(self, tenant: Any, sales_invoice_id: str) -> CustomerReceivable | None:
        return self.get_queryset(tenant).filter(sales_invoice_id=sales_invoice_id).first()

    def find_by_idempotency_key(self, tenant: Any, key: str) -> CustomerReceivable | None:
        if not key:
            return None
        return self.get_queryset(tenant).filter(idempotency_key=key).first()

    def create(self, tenant: Any, **kwargs: Any) -> CustomerReceivable:
        return CustomerReceivable.objects.create(tenant=tenant, **kwargs)


class CustomerPaymentRepository:
    """Repository encapsulating persistence operations for CustomerPayment entity."""

    def get_queryset(self, tenant: Any) -> QuerySet[CustomerPayment]:
        return CustomerPayment.objects.filter(tenant=tenant)

    def find_by_id(self, tenant: Any, payment_id: str) -> CustomerPayment | None:
        return self.get_queryset(tenant).filter(pk=payment_id).first()

    def find_by_idempotency_key(self, tenant: Any, key: str) -> CustomerPayment | None:
        if not key:
            return None
        return self.get_queryset(tenant).filter(idempotency_key=key).first()

    def create(self, tenant: Any, **kwargs: Any) -> CustomerPayment:
        return CustomerPayment.objects.create(tenant=tenant, **kwargs)
