"""Repository layer for Sales persistence."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.sales.models import (
    CashRegister,
    RegisterSession,
    SalesInvoice,
    SalesInvoiceLine,
    SalesPayment,
)


class SalesInvoiceRepository:
    """Repository encapsulating persistence operations for SalesInvoice."""

    def get_queryset(self, tenant: Any) -> QuerySet[SalesInvoice]:
        return SalesInvoice.objects.filter(tenant=tenant)

    def find_by_id(self, tenant: Any, invoice_id: str) -> SalesInvoice | None:
        return self.get_queryset(tenant).filter(pk=invoice_id).first()

    def find_by_idempotency_key(self, tenant: Any, key: str) -> SalesInvoice | None:
        if not key:
            return None
        return self.get_queryset(tenant).filter(idempotency_key=key).first()

    def create(self, tenant: Any, **kwargs: Any) -> SalesInvoice:
        return SalesInvoice.objects.create(tenant=tenant, **kwargs)


class SalesPaymentRepository:
    """Repository encapsulating persistence operations for SalesPayment."""

    def create(self, tenant: Any, **kwargs: Any) -> SalesPayment:
        return SalesPayment.objects.create(tenant=tenant, **kwargs)


class CashRegisterRepository:
    """Repository encapsulating persistence operations for CashRegister."""

    def get_queryset(self, tenant: Any) -> QuerySet[CashRegister]:
        return CashRegister.objects.filter(tenant=tenant)

    def create(self, tenant: Any, **kwargs: Any) -> CashRegister:
        return CashRegister.objects.create(tenant=tenant, **kwargs)


class RegisterSessionRepository:
    """Repository encapsulating persistence operations for RegisterSession."""

    def get_queryset(self, tenant: Any) -> QuerySet[RegisterSession]:
        return RegisterSession.objects.filter(tenant=tenant)

    def create(self, tenant: Any, **kwargs: Any) -> RegisterSession:
        return RegisterSession.objects.create(tenant=tenant, **kwargs)
