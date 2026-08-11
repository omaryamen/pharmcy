"""Repository layer for Accounts Payable persistence."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.accounts_payable.models import (
    AccountsPayableEntry,
    CreditApplication,
    InvoiceDispute,
    SupplierInvoice,
    SupplierInvoiceLine,
    SupplierPayment,
)


class SupplierInvoiceRepository:
    """Repository encapsulating persistence operations for SupplierInvoice."""

    def get_queryset(self, tenant: Any) -> QuerySet[SupplierInvoice]:
        return SupplierInvoice.objects.filter(tenant=tenant)

    def find_by_id(self, tenant: Any, invoice_id: str) -> SupplierInvoice | None:
        return self.get_queryset(tenant).filter(pk=invoice_id).first()

    def find_by_supplier_bill_number(self, tenant: Any, supplier_id: str, supplier_invoice_number: str) -> SupplierInvoice | None:
        return self.get_queryset(tenant).filter(
            supplier_id=supplier_id,
            supplier_invoice_number__iexact=supplier_invoice_number.strip(),
        ).first()

    def find_by_idempotency_key(self, tenant: Any, key: str) -> SupplierInvoice | None:
        if not key:
            return None
        return self.get_queryset(tenant).filter(idempotency_key=key).first()

    def create(self, tenant: Any, **kwargs: Any) -> SupplierInvoice:
        return SupplierInvoice.objects.create(tenant=tenant, **kwargs)


class AccountsPayableRepository:
    """Repository encapsulating persistence operations for AccountsPayableEntry."""

    def get_queryset(self, tenant: Any) -> QuerySet[AccountsPayableEntry]:
        return AccountsPayableEntry.objects.filter(tenant=tenant)

    def create(self, tenant: Any, **kwargs: Any) -> AccountsPayableEntry:
        return AccountsPayableEntry.objects.create(tenant=tenant, **kwargs)


class SupplierPaymentRepository:
    """Repository encapsulating persistence operations for SupplierPayment."""

    def get_queryset(self, tenant: Any) -> QuerySet[SupplierPayment]:
        return SupplierPayment.objects.filter(tenant=tenant)

    def find_by_idempotency_key(self, tenant: Any, key: str) -> SupplierPayment | None:
        if not key:
            return None
        return self.get_queryset(tenant).filter(idempotency_key=key).first()

    def create(self, tenant: Any, **kwargs: Any) -> SupplierPayment:
        return SupplierPayment.objects.create(tenant=tenant, **kwargs)


class CreditApplicationRepository:
    """Repository encapsulating persistence operations for CreditApplication."""

    def create(self, tenant: Any, **kwargs: Any) -> CreditApplication:
        return CreditApplication.objects.create(tenant=tenant, **kwargs)


class InvoiceDisputeRepository:
    """Repository encapsulating persistence operations for InvoiceDispute."""

    def create(self, tenant: Any, **kwargs: Any) -> InvoiceDispute:
        return InvoiceDispute.objects.create(tenant=tenant, **kwargs)
